from pydantic import BaseModel, Field, ConfigDict
from typing import Any, List, Optional
import time
import json


class SemanticPointer(BaseModel):
    """
    语义指针：自包含的参数语义描述。

    用于消解代词歧义，将模糊的参数描述转化为精确的语义实体。
    例如：将 "该用户的ID" 转化为 "昨天第二个需要退款资格检查的客户的ID"
    """
    model_config = ConfigDict(extra='allow')

    param_name: str                          # 参数名，如 "client_id"
    original_desc: str                       # 原始描述，如 "该用户的ID"
    resolved_desc: str                       # 补全后的描述
    confidence: float = 1.0                  # 置信度 (0-1)
    resolution_chain: List[str] = Field(default_factory=list)  # 解析链，记录每级补全的信息
    source_agent_path: List[str] = Field(default_factory=list) # 信息来源的 Agent 路径
    has_ambiguity: bool = False              # 是否包含模糊引用


class ContextEntry(BaseModel):
    """
    上下文条目：存储任务执行结果和元数据

    支持摘要模式：
    - summary: 结果摘要（用于 LLM 参数解析，减少 token 消耗）
    - value: 完整结果（按需展开）
    """
    value: Any
    source: str                 # 来源：如 "user_input", "agent_step_2", "tool_output_profile"
    task_path: str              # 产生该值的任务路径（用于追踪）
    timestamp: float = Field(default_factory=time.time)
    confidence: float = 1.0     # 可选：置信度（用于冲突消解）
    summary: Optional[str] = None  # 结果摘要（用于减少上下文传递大小）

    def get_summary(self, max_length: int = 300) -> str:
        """
        获取结果摘要，用于 LLM 参数解析

        Args:
            max_length: 摘要最大长度

        Returns:
            结果摘要字符串
        """
        if self.summary:
            return self.summary

        # 动态生成摘要
        return self._generate_summary(self.value, max_length)

    def _generate_summary(self, value: Any, max_length: int) -> str:
        """动态生成摘要"""
        if value is None:
            return "无结果"

        if isinstance(value, str):
            if len(value) <= max_length:
                return value
            return value[:max_length] + "..."

        if isinstance(value, dict):
            # 提取关键字段
            summary_parts = []

            # 状态信息
            if "status" in value:
                summary_parts.append(f"状态:{value['status']}")

            # 错误信息优先
            if "error" in value and value["error"]:
                return f"错误: {str(value['error'])[:100]}"

            # 提取结果摘要
            for key in ["message", "msg", "summary", "result", "output"]:
                if key in value and value[key]:
                    v = value[key]
                    if isinstance(v, str) and len(v) <= max_length:
                        summary_parts.append(v)
                        break
                    elif isinstance(v, str):
                        summary_parts.append(v[:max_length] + "...")
                        break

            if summary_parts:
                return " | ".join(summary_parts)

            # 降级：返回键列表
            keys = list(value.keys())[:5]
            return f"包含: {', '.join(keys)}" + ("..." if len(value) > 5 else "")

        if isinstance(value, list):
            return f"列表[{len(value)}项]"

        # 其他类型
        str_val = str(value)
        if len(str_val) <= max_length:
            return str_val
        return str_val[:max_length] + "..."

    def to_summary_dict(self) -> dict:
        """
        转换为摘要字典，用于 LLM 参数解析
        只包含摘要信息，不包含完整 value
        """
        return {
            "summary": self.get_summary(),
            "source": self.source,
            "task_path": self.task_path,
            "confidence": self.confidence
        }


def create_context_entry_with_summary(
    value: Any,
    source: str,
    task_path: str,
    max_summary_length: int = 300
) -> ContextEntry:
    """
    创建带摘要的 ContextEntry

    Args:
        value: 完整结果
        source: 数据来源
        task_path: 任务路径
        max_summary_length: 摘要最大长度

    Returns:
        带摘要的 ContextEntry
    """
    entry = ContextEntry(
        value=value,
        source=source,
        task_path=task_path,
        timestamp=time.time(),
        confidence=1.0
    )
    # 预生成摘要
    entry.summary = entry._generate_summary(value, max_summary_length)
    return entry