# api_server.py
"""
Flora多智能体协作系统 - API服务器实现（基于FastAPI）

FastAPI作为TaskRouter的HTTP接口，将HTTP JSON请求转换为任务请求，
通过TaskRouterClient统一路由到Actor系统。

注意：任务执行是异步的，API 立即返回 202 Accepted，
结果通过 RabbitMQ 推送给 interaction 服务，再通过 SSE 推送给前端。
"""

import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid

# 导入TaskRouter
from router import TaskRouterClient, init_task_router, get_task_router
from capabilities import init_capabilities
from capabilities.registry import capability_registry
from agents.tree.tree_manager import treeManager

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Flora 多智能体协作系统 API",
    description="Flora系统的RESTful API接口",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _init_task_router() -> None:
    """初始化 TaskRouterActor"""
    if getattr(app.state, "task_router", None):
        return

    from thespian.actors import ActorSystem

    # 创建 Actor 系统
    app.state.actor_system = ActorSystem('simpleSystemBase')

    # 初始化 TaskRouterActor 并获取客户端
    app.state.task_router = init_task_router(app.state.actor_system)
    logger.info("TaskRouterActor initialized.")


def _ensure_task_router() -> TaskRouterClient:
    """确保 TaskRouter 已初始化"""
    if not getattr(app.state, "task_router", None):
        _init_task_router()
    return app.state.task_router


def _ensure_capabilities_ready() -> None:
    missing = []
    for name in ("llm", "task_planning", "excution"):
        if not capability_registry.has_capability(name):
            missing.append(name)
    if missing:
        raise HTTPException(
            status_code=503,
            detail=f"Capabilities not ready: {', '.join(missing)}. Check tasks/config.json and API keys."
        )


@app.on_event("startup")
def _on_startup() -> None:
    init_capabilities()
    _init_task_router()


@app.on_event("shutdown")
def _on_shutdown() -> None:
    actor_system = getattr(app.state, "actor_system", None)
    if actor_system:
        try:
            actor_system.shutdown()
        except Exception:
            logger.exception("Failed to shutdown ActorSystem cleanly.")


# --- 定义请求体模型 (Pydantic) ---
class TaskRequest(BaseModel):
    user_input: str
    user_id: str
    agent_id: str | None = None
    trace_id: str | None = None
    task_path: str | None = None
    parameters: Dict[str, Any] | None = None


class ResumeRequest(BaseModel):
    trace_id: str  # 使用 trace_id 作为主键（整个链路的唯一标识）
    parameters: dict
    user_id: str
    task_path: str | None = None


class TaskStatusRequest(BaseModel):
    trace_id: str  # 使用 trace_id 查询状态


def _parse_user_id_payload(raw_user_id: str) -> tuple[str, dict]:
    """
    Parse user_id like "<userid:test_id,tenant_id:t_001>" into (user_id, params).
    """
    if not raw_user_id:
        return raw_user_id, {}

    text = raw_user_id.strip()
    if not (text.startswith("<") and text.endswith(">")):
        return raw_user_id, {}

    body = text[1:-1].strip()
    if not body:
        return raw_user_id, {}

    params = {}
    for part in body.split(","):
        chunk = part.strip()
        if not chunk or ":" not in chunk:
            continue
        key, value = chunk.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key or not value:
            continue
        params[key] = value

    aliases = {
        "userid": "user_id",
        "userId": "user_id",
        "tenantId": "tenant_id",
        "tenantID": "tenant_id",
        "activeId": "active_id",
        "activeID": "active_id",
    }
    for alias, canonical in aliases.items():
        if alias in params and canonical not in params:
            params[canonical] = params[alias]

    user_id = params.get("user_id") or raw_user_id
    return user_id, params


# --- 核心接口 1: 执行任务 ---
@app.post("/tasks/execute", status_code=202)
def execute_task(req: TaskRequest):
    """
    执行新任务（异步模式）

    任务会被提交到 Actor 系统异步执行，API 立即返回 202 Accepted。
    任务结果会通过 RabbitMQ 推送给 interaction 服务，再通过 SSE 推送给前端。

    Args:
        req: 任务请求，包含用户输入和用户ID

    Returns:
        202 Accepted: 任务已接受，包含 task_id 和 trace_id
    """
    try:
        _ensure_capabilities_ready()
        task_router = _ensure_task_router()

        # 解析 user_id
        user_id, embedded_params = _parse_user_id_payload(req.user_id)

        # 合并参数
        parameters = req.parameters or {}
        if embedded_params:
            parameters = {**embedded_params, **parameters}
            if "user_id" not in parameters:
                parameters["user_id"] = user_id

        # 通过 TaskRouterClient 提交任务（异步，不等待结果）
        result = task_router.submit_new_task(
            user_input=req.user_input,
            user_id=user_id,
            agent_id=req.agent_id,
            task_id=None,  # 自动生成
            trace_id=req.trace_id,
            task_path=req.task_path,
            parameters=parameters,
            timeout=5.0  # 只等待任务被接受，不等待执行完成
        )

        if result.get("accepted"):
            return JSONResponse(
                status_code=202,
                content={
                    "success": True,
                    "message": "Task accepted and processing",
                    "data": {
                        "task_id": result["task_id"],
                        "trace_id": result["trace_id"],
                        "status": "RUNNING"
                    }
                }
            )
        else:
            raise HTTPException(
                status_code=500,
                detail={
                    "success": False,
                    "error": result.get("error", "Failed to submit task")
                }
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing task: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "data": None,
                "error": str(e)
            }
        )


# --- 核心接口 2: 补充参数/恢复任务 ---
@app.post("/tasks/resume", status_code=202)
def resume_task(req: ResumeRequest):
    """
    恢复任务并补充参数（异步模式）

    任务会被提交到 Actor 系统异步执行，API 立即返回 202 Accepted。
    任务结果会通过 RabbitMQ 推送给 interaction 服务，再通过 SSE 推送给前端。

    Args:
        req: 恢复请求，包含 trace_id、补充参数和用户ID

    Returns:
        202 Accepted: 恢复请求已接受
    """
    try:
        _ensure_capabilities_ready()
        task_router = _ensure_task_router()

        # 通过 TaskRouterClient 提交恢复请求（异步，不等待结果）
        result = task_router.submit_resume_task(
            trace_id=req.trace_id,
            parameters=req.parameters,
            user_id=req.user_id,
            timeout=5.0  # 只等待请求被接受，不等待执行完成
        )

        if result.get("accepted"):
            return JSONResponse(
                status_code=202,
                content={
                    "success": True,
                    "message": "Resume request accepted and processing",
                    "data": {
                        "trace_id": result["trace_id"],
                        "status": "RUNNING"
                    }
                }
            )
        else:
            # 恢复失败（如任务不存在或状态不对）
            raise HTTPException(
                status_code=400,
                detail={
                    "success": False,
                    "error": result.get("error", "Failed to resume task")
                }
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming task: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "data": None,
                "error": str(e)
            }
        )


# --- 核心接口 3: 查询任务状态 ---
@app.get("/tasks/{trace_id}/status")
def get_task_status(trace_id: str):
    """
    查询任务状态

    Args:
        trace_id: 跟踪ID（整个链路的唯一标识）

    Returns:
        任务状态信息
    """
    try:
        task_router = _ensure_task_router()
        status = task_router.get_task_status(trace_id)

        if not status:
            raise HTTPException(status_code=404, detail=f"Task with trace_id={trace_id} not found")

        return {
            "success": True,
            "data": status,
            "error": None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "data": None,
                "error": str(e)
            }
        )


# --- 核心接口 4: 取消任务 ---
@app.post("/tasks/{trace_id}/cancel")
def cancel_task(trace_id: str):
    """
    取消任务

    Args:
        trace_id: 跟踪ID（整个链路的唯一标识）

    Returns:
        取消结果
    """
    try:
        task_router = _ensure_task_router()
        success = task_router.cancel_task(trace_id)

        return {
            "success": success,
            "data": {"trace_id": trace_id, "cancelled": success},
            "error": None if success else "Failed to cancel task"
        }

    except Exception as e:
        logger.error(f"Error cancelling task: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "data": None,
                "error": str(e)
            }
        )


# --- 健康检查端点 ---
@app.get("/health")
def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "flora-api-server"
    }


# --- 核心接口 5: 获取Agent子树 ---
@app.get("/agents/tree/subtree/{root_id}")
def get_agent_subtree(root_id: str):
    """
    获取以指定节点为根的Agent子树

    Args:
        root_id: 根节点Agent ID

    Returns:
        子树结构
    """
    try:
        subtree = treeManager.get_subtree(root_id)
        if not subtree:
            raise HTTPException(status_code=404, detail=f"Agent {root_id} not found")

        return {
            "success": True,
            "data": subtree,
            "error": None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting subtree for agent {root_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "data": None,
                "error": str(e)
            }
        )


# 工厂函数，用于创建API服务器实例
def create_api_server(config: dict = None) -> FastAPI:
    """
    创建API服务器实例

    Args:
        config: 服务器配置

    Returns:
        FastAPI应用实例
    """
    return app


# 如果直接运行此文件，则启动服务器
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Flora API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')

    args = parser.parse_args()

    # 配置日志
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger.info(f"Starting API server on {args.host}:{args.port}")
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.debug
    )
