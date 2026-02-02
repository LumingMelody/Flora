from typing import Dict, Any, Optional, List
from .interface import ISystemResponseManagerCapability
from common import (
    SystemResponseDTO,
    SuggestedActionDTO,
    ActionType,
    TaskStatusSummary
)
from ..llm.interface import ILLMCapability

class CommonSystemResponse(ISystemResponseManagerCapability):
    """系统响应管理器 - 统一生成系统响应，包括文本和结构化数据"""
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """初始化系统响应管理器"""
        self.logger.info("初始化系统响应管理器")
        self.config = config
        self._llm = None
        self.logger.info("系统响应管理器初始化完成")
        
    @property
    def llm(self):
        """懒加载LLM能力"""
        if self._llm is None:
            from .. import get_capability
            self._llm = get_capability("llm", expected_type=ILLMCapability)
        return self._llm
    
    def shutdown(self) -> None:
        """关闭系统响应管理器"""
        pass
    
    def get_capability_type(self) -> str:
        """返回能力类型"""
        return "response_generation"
    
    def generate_response(self, session_id: str, response_text: str, 
                         suggested_actions: List[SuggestedActionDTO] = None, 
                         task_status: Optional[TaskStatusSummary] = None, 
                         requires_input: bool = False, 
                         awaiting_slot: Optional[str] = None, 
                         display_data: Optional[Dict[str, Any]] = None) -> SystemResponseDTO:
        """生成系统响应
        
        Args:
            session_id: 会话ID
            response_text: 响应文本
            suggested_actions: 建议操作列表
            task_status: 任务状态摘要
            requires_input: 是否需要用户输入
            awaiting_slot: 正在等待的槽位
            display_data: 结构化展示数据
            
        Returns:
            系统响应DTO
        """
        return SystemResponseDTO(
            session_id=session_id,
            response_text=response_text,
            suggested_actions=suggested_actions or [],
            task_status=task_status,
            requires_input=requires_input,
            awaiting_slot=awaiting_slot,
            display_data=display_data
        )
    
    def generate_task_creation_response(self, session_id: str, task_id: str, task_title: str) -> SystemResponseDTO:
        """生成任务创建成功的响应
        
        Args:
            session_id: 会话ID
            task_id: 任务ID
            task_title: 任务标题
            
        Returns:
            系统响应DTO
        """
        fallback_text = f"任务 '{task_title}' 已成功创建，任务ID: {task_id}"
        
        # 使用 LLM 增强响应文本
        enhanced_text = self._enhance_text_with_llm(
            base_info={
                "task_title": task_title,
                "task_id": task_id,
                "fallback_text": fallback_text
            },
            context_type="task_creation"
        )
        
        # 生成建议操作
        suggested_actions = [
            SuggestedActionDTO(
                type=ActionType.QUERY,
                title="查看任务状态",
                payload=f"QUERY_TASK_{task_id}"
            ),
            SuggestedActionDTO(
                type=ActionType.CANCEL,
                title="取消任务",
                payload=f"CANCEL_TASK_{task_id}"
            )
        ]
        
        return self.generate_response(
            session_id=session_id,
            response_text=enhanced_text,
            suggested_actions=suggested_actions,
            requires_input=False
        )
    
    def generate_task_status_response(self, session_id: str, task_status_info: Dict[str, Any]) -> SystemResponseDTO:
        """生成任务状态响应
        
        Args:
            session_id: 会话ID
            task_status_info: 任务状态信息
            
        Returns:
            系统响应DTO
        """
        task_id = task_status_info["task_id"]
        status = task_status_info["status"]
        title = task_status_info["title"]
        progress = task_status_info["progress"]
        error_summary = task_status_info.get("error_summary", "")
        
        # 原始 fallback 文本（用于 LLM 失败时回退）
        if status == "RUNNING":
            fallback_text = f"任务 '{title}' 正在运行中，进度: {int(progress * 100)}%"
        elif status == "COMPLETED":
            fallback_text = f"任务 '{title}' 已成功完成"
        elif status == "FAILED":
            fallback_text = f"任务 '{title}' 执行失败，请检查日志"
        elif status == "PAUSED":
            fallback_text = f"任务 '{title}' 已暂停"
        elif status == "CANCELLED":
            fallback_text = f"任务 '{title}' 已取消"
        else:
            fallback_text = f"任务 '{title}' 状态: {status}"
        
        # 使用 LLM 增强
        enhanced_text = self._enhance_text_with_llm(
            base_info={
                "title": title,
                "status": status,
                "progress_percent": int(progress * 100),
                "error_summary": error_summary,
                "fallback_text": fallback_text
            },
            context_type="task_status"
        )
        
        # 生成建议操作
        suggested_actions = []
        if status == "RUNNING":
            suggested_actions.append(
                SuggestedActionDTO(
                    type=ActionType.PAUSE,
                    title="暂停任务",
                    payload=f"PAUSE_TASK_{task_id}"
                )
            )
        elif status == "PAUSED":
            suggested_actions.append(
                SuggestedActionDTO(
                    type=ActionType.RESUME,
                    title="恢复任务",
                    payload=f"RESUME_TASK_{task_id}"
                )
            )
        
        suggested_actions.extend([
            SuggestedActionDTO(
                type=ActionType.QUERY,
                title="查看详细日志",
                payload=f"QUERY_TASK_LOGS_{task_id}"
            ),
            SuggestedActionDTO(
                type=ActionType.CANCEL,
                title="取消任务",
                payload=f"CANCEL_TASK_{task_id}"
            )
        ])
        
        # 生成任务状态摘要
        task_status = TaskStatusSummary(
            task_id=task_id,
            status=status,
            progress=progress,
            message=enhanced_text
        )
        
        return self.generate_response(
            session_id=session_id,
            response_text=enhanced_text,
            suggested_actions=suggested_actions,
            task_status=task_status,
            requires_input=False,
            display_data=task_status_info
        )
    
    def generate_fill_slot_response(self, session_id: str, missing_slots: List[str], draft_id: str) -> SystemResponseDTO:
        """生成填槽请求响应
        
        Args:
            session_id: 会话ID
            missing_slots: 缺失的槽位列表
            draft_id: 草稿ID
            
        Returns:
            系统响应DTO
        """
        # 槽位示例值映射
        slot_examples = {
            "task_name": "数据分析报告",
            "target_url": "https://example.com",
            "start_time": "每天上午9点",
            "end_time": "每天下午5点",
            "frequency": "每天一次",
            "max_runs": "10次"
        }
        
        if missing_slots:
            current_slot = missing_slots[0]
            slot_display = self._get_slot_display_name(current_slot)
            example_value = slot_examples.get(current_slot, "相关信息")
            fallback_text = f"请提供 {slot_display}"
            
            # 使用 LLM 增强
            enhanced_text = self._enhance_text_with_llm(
                base_info={
                    "slot_display_name": slot_display, 
                    "example_value": example_value,
                    "fallback_text": fallback_text
                },
                context_type="slot_fill"
            )
            
            # 生成建议操作
            suggested_actions = [
                SuggestedActionDTO(
                    type=ActionType.CANCEL,
                    title="取消任务",
                    payload=f"CANCEL_DRAFT_{draft_id}"
                )
            ]
            
            return self.generate_response(
                session_id=session_id,
                response_text=enhanced_text,
                suggested_actions=suggested_actions,
                requires_input=True,
                awaiting_slot=current_slot
            )
        
        # 如果没有缺失槽位，请求确认
        fallback_text = "请确认任务信息是否正确？"
        # 使用 LLM 增强
        enhanced_text = self._enhance_text_with_llm(
            base_info={"fallback_text": fallback_text},
            context_type="default"
        )
        
        # 生成建议操作
        suggested_actions = [
            SuggestedActionDTO(
                type=ActionType.CONFIRM,
                title="确认执行",
                payload=f"CONFIRM_DRAFT_{draft_id}"
            ),
            SuggestedActionDTO(
                type=ActionType.CANCEL,
                title="取消任务",
                payload=f"CANCEL_DRAFT_{draft_id}"
            ),
            SuggestedActionDTO(
                type=ActionType.MODIFY,
                title="修改信息",
                payload=f"MODIFY_DRAFT_{draft_id}"
            )
        ]
        
        return self.generate_response(
            session_id=session_id,
            response_text=enhanced_text,
            suggested_actions=suggested_actions,
            requires_input=True
        )
    
    def generate_query_response(self, session_id: str, query_result: Dict[str, Any]) -> SystemResponseDTO:
        """生成查询结果响应
        
        Args:
            session_id: 会话ID
            query_result: 查询结果
            
        Returns:
            系统响应DTO
        """
        total = query_result.get("total", 0)
        tasks = query_result.get("tasks", [])
        
        fallback_text = f"找到 {total} 个任务" if total > 0 else "没有找到匹配的任务"
        
        # 使用 LLM 增强
        enhanced_text = self._enhance_text_with_llm(
            base_info={
                "total": total,
                "tasks": tasks,
                "fallback_text": fallback_text
            },
            context_type="query_result"
        )
        
        # 生成建议操作
        suggested_actions = [
            SuggestedActionDTO(
                type=ActionType.QUERY,
                title="查看详情",
                payload=f"QUERY_TASK_DETAIL_{tasks[0]['task_id']}"
            ) if tasks else None
        ]
        
        # 过滤掉None值
        suggested_actions = [action for action in suggested_actions if action]
        
        return self.generate_response(
            session_id=session_id,
            response_text=enhanced_text,
            suggested_actions=suggested_actions,
            requires_input=False,
            display_data=query_result
        )
    
    def generate_error_response(self, session_id: str, error_message: str) -> SystemResponseDTO:
        """生成错误响应
        
        Args:
            session_id: 会话ID
            error_message: 错误信息
            
        Returns:
            系统响应DTO
        """
        fallback_text = f"抱歉，发生了错误：{error_message}"
        
        # 使用 LLM 增强
        enhanced_text = self._enhance_text_with_llm(
            base_info={"error_message": error_message, "fallback_text": fallback_text},
            context_type="error"
        )

        # 生成建议操作
        suggested_actions = [
            SuggestedActionDTO(
                type=ActionType.RETRY,
                title="重试",
                payload="RETRY_OPERATION"
            ),
            SuggestedActionDTO(
                type=ActionType.CANCEL,
                title="取消",
                payload="CANCEL_OPERATION"
            )
        ]

        return self.generate_response(
            session_id=session_id,
            response_text=enhanced_text,
            suggested_actions=suggested_actions,
            requires_input=False
        )
    
    def generate_idle_response(self, session_id: str, idle_message: str) -> SystemResponseDTO:
        """生成闲聊模式响应
        
        Args:
            session_id: 会话ID
            idle_message: 闲聊消息
            
        Returns:
            系统响应DTO
        """
        fallback_text = idle_message
        
        # 使用 LLM 增强
        enhanced_text = self._enhance_text_with_llm(
            base_info={"fallback_text": fallback_text},
            context_type="idle"
        )
        
        return self.generate_response(
            session_id=session_id,
            response_text=enhanced_text,
            requires_input=True
        )
    
    def _enhance_text_with_llm(
        self,
        base_info: Dict[str, Any],
        context_type: str = "default"
    ) -> str:
        """
        使用 LLM 增强响应文本的人性化程度，生成 Markdown 格式输出
        
        Args:
            base_info: 包含原始信息的字典（如 task_title, status, progress 等）
            context_type: 上下文类型，用于定制 prompt（如 "task_status", "error", "slot_fill"）
        
        Returns:
            增强后的 Markdown 格式响应文本
        """
        if not self.llm:
            # 若未初始化 LLM，回退到原始文本
            return base_info.get("fallback_text", "系统消息")

        # 根据 context_type 构造 prompt
        prompts = {
            "task_creation": (
                "你是一个温暖、专业的任务助手。请根据以下信息，生成 Markdown 格式的任务创建成功响应。\n"
                "要求：\n"
                "- 开头使用 🎉 表情符号\n"
                "- 任务名称用 **加粗** 突出显示\n"
                "- 任务 ID 用 `代码格式` 展示\n"
                "- 语气要像朋友一样亲切，避免机械感\n"
                "- 包含一句后续操作的引导语\n"
                "- 只输出 Markdown 内容，不要添加任何解释\n\n"
                f"任务标题：{base_info['title']}\n"
                f"任务ID：{base_info['task_id']}\n"
            ),
            "task_status": (
                "你是一个温暖、专业的任务助手。请根据以下信息，生成 Markdown 格式的任务状态响应。\n"
                "要求：\n"
                "- 使用合适的表情符号开头（成功→✨，运行中→⏳，失败→😟，暂停→⏸️，取消→❌）\n"
                "- 任务名称用 **加粗** 突出显示\n"
                "- 进度百分比用 **加粗** 展示\n"
                "- 语气要亲切、有温度，根据状态调整情绪（成功时鼓励，失败时共情，等待时安抚）\n"
                "- 加入适当的空行创造呼吸感\n"
                "- 只输出 Markdown 内容，不要添加任何解释\n\n"
                f"任务标题：{base_info['title']}\n"
                f"状态：{base_info['status']}\n"
                f"进度百分比：{base_info.get('progress_percent', 0)}\n"
                f"错误摘要（如有）：{base_info.get('error_summary', '')}\n"
            ),
            "error": (
                "你是一位体贴的客服助手。请根据以下错误信息，生成 Markdown 格式的友好提示。\n"
                "要求：\n"
                "- 开头使用 ⚠️ 或 😟 表情符号\n"
                "- 错误信息用 > 引用块包裹\n"
                "- 提供 1~2 条行动建议，用 - 列表展示\n"
                "- 结尾给予鼓励和支持\n"
                "- 语气亲切，避免推卸责任\n"
                "- 加入适当的空行创造呼吸感\n"
                "- 只输出 Markdown 内容，不要添加任何解释\n\n"
                f"原始错误：{base_info['error_message']}\n"
            ),
            "slot_fill": (
                "你是一位耐心的引导者。请根据以下信息，生成 Markdown 格式的填槽请求响应。\n"
                "要求：\n"
                "- 开头使用 📝 表情符号\n"
                "- 缺失的字段名称用 **加粗** 突出显示\n"
                "- 给出简单的示例（用括号包裹，如 `(例如：每天上午9点)`）\n"
                "- 语气轻松、亲切，带有鼓励\n"
                "- 只输出 Markdown 内容，不要添加任何解释\n\n"
                f"缺失字段显示名：{base_info['slot_display_name']}\n"
                f"示例值：{base_info.get('example_value', '相关信息')}\n"
            ),
            "confirm_draft": (
                "你是一位专业的任务助手。请根据以下草稿信息，生成 Markdown 格式的确认请求响应。\n"
                "要求：\n"
                "- 开头使用 🔍 表情符号\n"
                "- 用 - 列表展示关键任务信息\n"
                "- 适当突出重要信息\n"
                "- 结尾引导用户点击确认按钮\n"
                "- 语气亲切，充满信任感\n"
                "- 加入适当的空行创造呼吸感\n"
                "- 只输出 Markdown 内容，不要添加任何解释\n\n"
                f"草稿信息：{base_info['draft_info']}\n"
            ),
            "query_result": (
                "你是一个友好的查询助手。请根据以下查询结果，生成 Markdown 格式的响应。\n"
                "要求：\n"
                "- 开头使用合适的表情符号（有结果→📊，无结果→🕳️）\n"
                "- 总任务数用 **加粗** 突出显示\n"
                "- 如果有任务，列出最近一个任务的标题（**加粗**）、ID（`代码格式`）和状态\n"
                "- 状态表情符号映射：RUNNING→⏳, COMPLETED→✅, FAILED→❌, PAUSED→⏸️, CANCELLED→❌\n"
                "- 语气亲切，带有引导性\n"
                "- 加入适当的空行创造呼吸感\n"
                "- 只输出 Markdown 内容，不要添加任何解释\n\n"
                f"总任务数：{base_info['total']}\n"
                f"任务列表（字典列表）：{base_info.get('tasks', [])}\n"
            ),
            "idle": (
                "你是一个友好的聊天助手。请将以下空闲消息改写成一句自然、流畅、友好的 Markdown 格式回复。\n"
                "要求：\n"
                "- 加入合适的表情符号\n"
                "- 语气亲切，像朋友一样\n"
                "- 只输出 Markdown 内容，不要添加任何解释\n\n"
                f"原始消息：{base_info['fallback_text']}\n"
            ),
            "need_input": (
                "你是一个耐心的任务助手。任务执行过程中需要用户补充一些信息。请根据以下内容生成友好的提示消息。\n"
                "要求：\n"
                "- 使用 📋 和 📝 表情符号区分已收集和待补充的信息\n"
                "- 已收集的信息用列表展示，参数名**加粗**\n"
                "- 待补充的信息用列表展示，突出显示\n"
                "- 语气亲切、耐心，引导用户提供信息\n"
                "- 结尾提示用户可以直接输入信息或选择取消\n"
                "- 只输出 Markdown 内容，不要添加任何解释\n\n"
                f"已收集的参数：{base_info.get('completed_params', {})}\n"
                f"待补充的参数：{base_info.get('missing_params', [])}\n"
            ),
            "default": (
                "请将以下系统消息改写成一句自然、流畅、对用户友好的 Markdown 格式文本。\n"
                "要求：\n"
                "- 加入合适的表情符号\n"
                "- 突出关键信息\n"
                "- 语气亲切，避免机械感\n"
                "- 只输出 Markdown 内容，不要添加任何解释\n\n"
                f"原始消息：{base_info['fallback_text']}\n"
            )
        }

        prompt = prompts.get(context_type, prompts["default"])
        
        try:
            enhanced = self.llm.generate(prompt, max_tokens=120, temperature=0.6)
            # 清理多余引号或解释
            text = enhanced.strip()
            if text.startswith(('"', "'", "\"")) and text.endswith(('"', "'", "\"")):
                text = text[1:-1]
            return text
        except Exception as e:
            # LLM 调用失败时回退
            return base_info.get("fallback_text", "系统消息")
    
    def _get_slot_display_name(self, slot_name: str) -> str:
        """获取槽位的显示名称
        
        Args:
            slot_name: 槽位名称
            
        Returns:
            槽位的显示名称
        """
        # 槽位名称映射，实际应该从配置或数据库中获取
        slot_display_names = {
            "task_name": "任务名称",
            "target_url": "目标网址",
            "start_time": "开始时间",
            "end_time": "结束时间",
            "frequency": "执行频率",
            "max_runs": "最大执行次数"
        }
        
        return slot_display_names.get(slot_name, slot_name)

    def generate_need_input_response(
        self,
        session_id: str,
        trace_id: str,
        missing_params: list,
        completed_params: dict = None
    ) -> SystemResponseDTO:
        """生成任务需要输入的响应（NEED_INPUT 状态）

        Args:
            session_id: 会话ID
            trace_id: 任务的 trace_id
            missing_params: 缺失的参数列表
            completed_params: 已完成的参数字典

        Returns:
            系统响应DTO，包含自然语言格式的提示和建议操作
        """
        completed_params = completed_params or {}

        # 构建自然语言消息
        message_parts = []

        # 已收集的信息
        if completed_params:
            message_parts.append("📋 **已收集的信息：**")
            for key, value in completed_params.items():
                display_key = self._get_param_display_name(key)
                display_value = self._format_param_value(value)
                message_parts.append(f"  • {display_key}：{display_value}")

        # 缺失的信息
        if missing_params:
            if message_parts:
                message_parts.append("")  # 空行分隔
            message_parts.append("📝 **还需要您提供：**")
            for param in missing_params:
                if isinstance(param, str):
                    display_name = self._get_param_display_name(param)
                    message_parts.append(f"  • {display_name}")
                elif isinstance(param, dict):
                    param_name = param.get("name", param.get("key", "未知参数"))
                    display_name = self._get_param_display_name(param_name)
                    message_parts.append(f"  • {display_name}")

            message_parts.append("")
            message_parts.append("请直接输入上述信息，或选择下方操作。")

        response_text = "\n".join(message_parts) if message_parts else "任务需要更多信息才能继续，请补充相关内容。"

        # 使用 LLM 美化（可选）
        enhanced_text = self._enhance_text_with_llm(
            base_info={
                "fallback_text": response_text,
                "missing_params": [self._get_param_display_name(p) if isinstance(p, str) else str(p) for p in missing_params],
                "completed_params": {self._get_param_display_name(k): self._format_param_value(v) for k, v in completed_params.items()}
            },
            context_type="need_input"
        )

        # 生成建议操作
        suggested_actions = [
            SuggestedActionDTO(
                type=ActionType.CANCEL,
                title="取消任务",
                payload=f"CANCEL_TASK_{trace_id}"
            )
        ]

        return self.generate_response(
            session_id=session_id,
            response_text=enhanced_text,
            suggested_actions=suggested_actions,
            requires_input=True,
            awaiting_slot=missing_params[0] if missing_params else None
        )

    def _get_param_display_name(self, param_name: str) -> str:
        """获取参数的显示名称

        Args:
            param_name: 参数名

        Returns:
            用户友好的显示名称
        """
        # 常见参数名映射
        display_names = {
            "user_id": "用户ID",
            "tenant_id": "租户ID",
            "active_id": "活动ID",
            "task_name": "任务名称",
            "target_url": "目标网址",
            "start_time": "开始时间",
            "end_time": "结束时间",
            "frequency": "执行频率",
            "max_runs": "最大执行次数",
            "description": "描述",
            "content": "内容",
            "title": "标题",
            "name": "名称",
            "email": "邮箱",
            "phone": "电话",
            "address": "地址",
            "amount": "金额",
            "quantity": "数量",
            "date": "日期",
            "time": "时间",
            "type": "类型",
            "status": "状态",
            "reason": "原因",
            "comment": "备注",
            "file": "文件",
            "image": "图片",
            "url": "链接",
            "code": "验证码",
            "password": "密码",
            "username": "用户名",
            "account": "账号",
        }

        # 先尝试精确匹配
        if param_name.lower() in display_names:
            return display_names[param_name.lower()]

        # 尝试部分匹配
        param_lower = param_name.lower()
        for key, value in display_names.items():
            if key in param_lower or param_lower in key:
                return value

        # 返回原始名称（首字母大写，下划线转空格）
        return param_name.replace("_", " ").title()

    def _format_param_value(self, value) -> str:
        """格式化参数值用于显示

        Args:
            value: 参数值

        Returns:
            格式化后的字符串
        """
        if value is None:
            return "未设置"
        if isinstance(value, bool):
            return "是" if value else "否"
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, str):
            if len(value) > 50:
                return value[:50] + "..."
            return value
        if isinstance(value, list):
            if len(value) == 0:
                return "空列表"
            return f"{len(value)} 项"
        if isinstance(value, dict):
            return f"{len(value)} 个字段"
        return str(value)[:50]