"""
任务结果处理服务

处理从 RabbitMQ 接收到的任务结果：
1. 根据 trace_id 查找对应的 session_id
2. 将结果存储到对话历史
3. 通过 SSE 推送给前端
"""
import logging
import json
import asyncio
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timezone

from external.database.dialog_state_repo import DialogStateRepository

logger = logging.getLogger(__name__)


class TaskResultHandler:
    """
    任务结果处理器

    负责处理任务执行结果，更新对话状态并推送 SSE 事件
    """

    def __init__(
        self,
        dialog_repo: DialogStateRepository,
        session_queues: Dict[str, asyncio.Queue],
        event_loop: Optional[asyncio.AbstractEventLoop] = None
    ):
        """
        初始化任务结果处理器

        Args:
            dialog_repo: 对话状态仓库
            session_queues: 会话级别的 SSE 事件队列（来自 api_server.py 的 SESSION_QUEUES）
            event_loop: 异步事件循环（用于在同步回调中调度异步任务）
        """
        self.dialog_repo = dialog_repo
        self.session_queues = session_queues
        self.event_loop = event_loop

    def handle_task_result(self, result: Dict[str, Any]) -> None:
        """
        处理任务结果（同步方法，供 RabbitMQ 回调使用）

        Args:
            result: 任务结果，格式：
                {
                    "trace_id": "xxx",
                    "status": "SUCCESS" | "FAILED",
                    "result": "任务结果文本",
                    "error": "错误信息（可选）",
                    "received_at": "ISO时间戳"
                }
        """
        trace_id = result.get("trace_id")
        if not trace_id:
            logger.warning("Task result missing trace_id")
            return

        # 1. 根据 trace_id 查找 session_id
        session_id = self.dialog_repo.get_session_by_trace(trace_id)
        if not session_id:
            logger.warning(f"No session found for trace_id: {trace_id}")
            return

        logger.info(f"Processing task result for trace_id={trace_id}, session_id={session_id}")

        # 2. 获取完整的映射信息（包含 user_id）
        mapping = self.dialog_repo.get_trace_mapping(trace_id)
        user_id = mapping.get("user_id") if mapping else None

        # 3. 构建 SSE 事件
        status = result.get("status", "UNKNOWN")
        task_result = result.get("result", "")
        error = result.get("error")

        sse_event = {
            "event": "task_result",
            "data": json.dumps({
                "trace_id": trace_id,
                "status": status,
                "result": task_result,
                "error": error,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }, ensure_ascii=False)
        }

        # 4. 推送 SSE 事件到对应的 session 队列
        # 注意：SESSION_QUEUES 是 defaultdict(asyncio.Queue)，访问时会自动创建队列
        # 即使前端 SSE 连接暂时断开，消息也会被缓存在队列中，等待重连后消费
        try:
            if self.event_loop and self.event_loop.is_running():
                # 在异步事件循环中调度
                asyncio.run_coroutine_threadsafe(
                    self._push_to_queue(session_id, sse_event),
                    self.event_loop
                )
            else:
                # 尝试直接放入队列（如果队列支持线程安全操作）
                self.session_queues[session_id].put_nowait(sse_event)
            logger.info(f"Pushed task result to SSE queue for session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to push SSE event: {e}")

        # 5. 更新对话状态（可选：将任务结果添加到对话历史）
        self._update_dialog_state(session_id, trace_id, status, task_result, error)

    async def _push_to_queue(self, session_id: str, event: Dict[str, Any]) -> None:
        """异步推送事件到队列"""
        await self.session_queues[session_id].put(event)

    def _update_dialog_state(
        self,
        session_id: str,
        trace_id: str,
        status: str,
        result: str,
        error: Optional[str]
    ) -> None:
        """
        更新对话状态，并将任务结果保存到对话历史

        将任务结果记录到对话状态中，确保用户刷新页面后仍能看到结果
        """
        try:
            dialog_state = self.dialog_repo.get_dialog_state(session_id)
            if not dialog_state:
                logger.warning(f"Dialog state not found for session: {session_id}")
                return

            # 更新 active_task_execution 状态
            if dialog_state.active_task_execution:
                # 任务已完成，清除活跃任务标记
                dialog_state.active_task_execution = None

            # 更新 last_updated
            dialog_state.last_updated = datetime.now(timezone.utc)

            # 保存更新
            self.dialog_repo.update_dialog_state(dialog_state)

            # 将任务结果保存到对话历史
            self._save_result_to_history(session_id, dialog_state.user_id, status, result, error)

            logger.debug(f"Updated dialog state for session: {session_id}")

        except Exception as e:
            logger.error(f"Failed to update dialog state: {e}", exc_info=True)

    def _save_result_to_history(
        self,
        session_id: str,
        user_id: str,
        status: str,
        result: Any,
        error: Optional[str]
    ) -> None:
        """
        将任务结果保存到对话历史

        这样即使 SSE 断开，用户刷新页面后也能看到任务结果
        """
        try:
            from capabilities.context_manager.interface import IContextManagerCapability
            from capabilities.registry import capability_registry
            from common.dialog import DialogTurn

            context_manager = capability_registry.get_capability("context_manager", IContextManagerCapability)

            # 构建结果消息（确保是字符串）
            if status == "SUCCESS":
                if result is None:
                    content = "任务执行完成"
                elif isinstance(result, str):
                    content = result
                elif isinstance(result, dict):
                    # 如果是字典，尝试提取有意义的内容或转为 JSON 字符串
                    content = json.dumps(result, ensure_ascii=False, indent=2)
                else:
                    content = str(result)
            else:
                content = f"任务执行失败: {error or '未知错误'}"

            # 创建系统消息
            system_turn = DialogTurn(
                session_id=session_id,
                user_id=user_id or "",
                role="system",
                utterance=content
            )

            # 保存到对话历史
            context_manager.add_turn(system_turn)
            logger.info(f"Saved task result to dialog history for session: {session_id}")

        except Exception as e:
            logger.warning(f"Failed to save task result to history: {e}")


# 全局单例
_task_result_handler: Optional[TaskResultHandler] = None


def get_task_result_handler() -> Optional[TaskResultHandler]:
    """获取任务结果处理器单例"""
    return _task_result_handler


def init_task_result_handler(
    dialog_repo: DialogStateRepository,
    session_queues: Dict[str, asyncio.Queue],
    event_loop: Optional[asyncio.AbstractEventLoop] = None
) -> TaskResultHandler:
    """
    初始化任务结果处理器

    Args:
        dialog_repo: 对话状态仓库
        session_queues: 会话级别的 SSE 事件队列
        event_loop: 异步事件循环

    Returns:
        TaskResultHandler 实例
    """
    global _task_result_handler
    _task_result_handler = TaskResultHandler(
        dialog_repo=dialog_repo,
        session_queues=session_queues,
        event_loop=event_loop
    )
    return _task_result_handler
