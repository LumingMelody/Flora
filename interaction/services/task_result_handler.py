"""
任务结果处理服务

处理从 RabbitMQ 接收到的任务结果：
1. 根据 trace_id 查找对应的 session_id
2. 使用 ISystemResponseManagerCapability 格式化结果
3. 将结果存储到对话历史
4. 通过 SSE 推送给前端
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
                    "status": "SUCCESS" | "FAILED" | "NEED_INPUT",
                    "result": "任务结果文本或结构化数据",
                    "error": "错误信息（可选）",
                    "need_input": { ... }（可选，当 status 为 NEED_INPUT 时）
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

        # 3. 获取状态和结果
        status = result.get("status", "UNKNOWN")
        task_result = result.get("result", "")
        error = result.get("error")
        need_input = result.get("need_input")

        # 4. 使用 SystemResponseManager 格式化结果
        formatted_content = self._format_result_with_response_manager(
            session_id, status, task_result, error, need_input
        )

        # 5. 构建 SSE 事件
        sse_event = {
            "event": "task_result",
            "data": json.dumps({
                "trace_id": trace_id,
                "status": status,
                "result": formatted_content,
                "error": error,
                "need_input": need_input,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }, ensure_ascii=False)
        }

        # 6. 推送 SSE 事件到对应的 session 队列
        try:
            if self.event_loop and self.event_loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    self._push_to_queue(session_id, sse_event),
                    self.event_loop
                )
            else:
                self.session_queues[session_id].put_nowait(sse_event)
            logger.info(f"Pushed task result to SSE queue for session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to push SSE event: {e}")

        # 7. 更新对话状态并保存到历史
        self._update_dialog_state(session_id, trace_id, status, formatted_content, error)

    def _format_result_with_response_manager(
        self,
        session_id: str,
        status: str,
        result: Any,
        error: Optional[str],
        need_input: Optional[Dict[str, Any]]
    ) -> str:
        """
        使用 ISystemResponseManagerCapability 格式化任务结果

        Args:
            session_id: 会话ID
            status: 任务状态
            result: 原始任务结果
            error: 错误信息
            need_input: 需要用户输入的信息

        Returns:
            格式化后的用户友好消息
        """
        try:
            from capabilities.system_response_manager.interface import ISystemResponseManagerCapability
            from capabilities.registry import capability_registry

            response_manager = capability_registry.get_capability(
                "system_response", ISystemResponseManagerCapability
            )

            # 根据状态选择不同的格式化方式
            if status == "NEED_INPUT" and need_input:
                # 需要用户输入
                slot_name = need_input.get("slot_name", "信息")
                prompt = need_input.get("prompt", f"请提供 {slot_name}")
                response = response_manager.generate_fill_slot_response(
                    session_id=session_id,
                    missing_slots=[slot_name],
                    draft_id=need_input.get("task_id", "")
                )
                return response.response_text or prompt

            elif status == "SUCCESS":
                # 成功：提取并格式化结果
                formatted = self._extract_meaningful_result(result)
                response = response_manager.generate_response(
                    session_id=session_id,
                    response_text=formatted
                )
                return response.response_text or formatted

            elif status in ("FAILED", "ERROR"):
                # 失败
                response = response_manager.generate_error_response(
                    session_id=session_id,
                    error_message=error or "任务执行失败"
                )
                return response.response_text or f"任务执行失败: {error or '未知错误'}"

            else:
                # 其他状态
                return self._extract_meaningful_result(result)

        except Exception as e:
            logger.warning(f"Failed to use SystemResponseManager, falling back: {e}")
            # 降级：直接格式化
            return self._extract_meaningful_result(result)

    def _extract_meaningful_result(self, result: Any) -> str:
        """
        从复杂的任务结果中提取有意义的内容

        处理嵌套的 step_results 结构，提取最终结果

        Args:
            result: 原始任务结果

        Returns:
            提取后的字符串结果
        """
        if result is None:
            return "任务执行完成"

        if isinstance(result, str):
            # 尝试解析 JSON 字符串
            try:
                parsed = json.loads(result)
                return self._extract_meaningful_result(parsed)
            except (json.JSONDecodeError, TypeError):
                return result

        if isinstance(result, dict):
            # 处理嵌套的 step_results
            if "step_results" in result:
                return self._summarize_step_results(result["step_results"])

            # 处理单个步骤结果
            if "status" in result and "result" in result:
                if result["status"] == "SUCCESS":
                    return self._extract_meaningful_result(result["result"])
                elif result["status"] == "ERROR":
                    return f"执行出错: {result.get('error', '未知错误')}"

            # 处理 Dify 工作流返回的结果
            if "code" in result and "data" in result:
                if result["code"] == 200 and result["data"]:
                    return self._extract_meaningful_result(result["data"])
                elif result.get("msg"):
                    return result["msg"]

            # 其他字典：尝试提取关键字段
            for key in ["result", "output", "response", "message", "content", "data"]:
                if key in result and result[key]:
                    return self._extract_meaningful_result(result[key])

            # 无法提取，返回简化的 JSON
            return self._simplify_dict_for_display(result)

        if isinstance(result, list):
            if len(result) == 0:
                return "无结果"
            if len(result) == 1:
                return self._extract_meaningful_result(result[0])
            # 多个结果，提取每个的摘要
            summaries = [self._extract_meaningful_result(item) for item in result[:5]]
            return "\n".join(f"• {s}" for s in summaries if s)

        return str(result)

    def _summarize_step_results(self, step_results: Dict[str, Any]) -> str:
        """
        汇总多个步骤的执行结果

        Args:
            step_results: 步骤结果字典

        Returns:
            汇总后的字符串
        """
        summaries = []
        success_count = 0
        error_count = 0

        for step_name, step_result in step_results.items():
            if isinstance(step_result, dict):
                status = step_result.get("status", "UNKNOWN")
                if status == "SUCCESS":
                    success_count += 1
                    # 提取成功结果的摘要
                    result_content = step_result.get("result")
                    if result_content:
                        summary = self._extract_meaningful_result(result_content)
                        if summary and len(summary) < 200:
                            summaries.append(summary)
                elif status == "ERROR":
                    error_count += 1
                elif "step_results" in step_result:
                    # 递归处理嵌套的 step_results
                    nested_summary = self._summarize_step_results(step_result["step_results"])
                    if nested_summary:
                        summaries.append(nested_summary)

        # 构建最终摘要
        if error_count > 0 and success_count == 0:
            return f"任务执行失败，共 {error_count} 个步骤出错"
        elif summaries:
            # 返回最有意义的摘要（通常是最后一个成功的结果）
            return summaries[-1] if summaries else "任务执行完成"
        else:
            return f"任务执行完成，成功 {success_count} 步"

    def _simplify_dict_for_display(self, d: Dict[str, Any], max_depth: int = 2) -> str:
        """
        简化字典用于显示

        Args:
            d: 原始字典
            max_depth: 最大深度

        Returns:
            简化后的字符串
        """
        if max_depth <= 0:
            return "..."

        simplified = {}
        for k, v in list(d.items())[:5]:  # 最多显示5个字段
            if isinstance(v, dict):
                simplified[k] = self._simplify_dict_for_display(v, max_depth - 1)
            elif isinstance(v, list):
                simplified[k] = f"[{len(v)} items]"
            elif isinstance(v, str) and len(v) > 100:
                simplified[k] = v[:100] + "..."
            else:
                simplified[k] = v

        try:
            return json.dumps(simplified, ensure_ascii=False, indent=2)
        except Exception:
            return str(simplified)

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

            # 将任务结果保存到对话历史（result 已经是格式化后的字符串）
            self._save_result_to_history(session_id, dialog_state.user_id, status, result, error)

            logger.debug(f"Updated dialog state for session: {session_id}")

        except Exception as e:
            logger.error(f"Failed to update dialog state: {e}", exc_info=True)

    def _save_result_to_history(
        self,
        session_id: str,
        user_id: str,
        status: str,
        result: str,
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

            # result 已经是格式化后的字符串
            content = result if isinstance(result, str) else str(result)

            # 如果是错误状态且 content 不包含错误信息，添加错误前缀
            if status in ("FAILED", "ERROR") and error and error not in content:
                content = f"任务执行失败: {error}"

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
