# agent_plan_cache.py
"""Agent 规划缓存数据结构"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import time
import uuid


@dataclass
class AgentPlanCache:
    """
    单个 Agent 的规划缓存

    存储某个 Agent 针对特定类型任务的规划结果，
    用于下次遇到相似任务时直接复用，跳过 LLM 规划。
    """
    # 标识
    cache_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""                      # 所属 Agent
    user_id: str = ""                       # 所属用户（可为空表示全局）

    # 触发条件
    task_description: str = ""              # 原始任务描述
    intent_pattern: str = ""                # 意图模式（正则，可选）
    trigger_keywords: List[str] = field(default_factory=list)  # 触发关键词

    # 规划结果（局部 Plan）
    plan: List[Dict[str, Any]] = field(default_factory=list)
    # 示例：
    # [
    #   {"step": 1, "type": "MCP", "executor": "get_user_profile", "description": "..."},
    #   {"step": 2, "type": "AGENT", "executor": "user_strat_fission", "description": "..."}
    # ]

    # 统计信息
    success_count: int = 0                  # 成功执行次数
    failure_count: int = 0                  # 失败执行次数
    confidence: float = 0.5                 # 置信度 (0.0 - 1.0)

    # 时间戳
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)

    # 状态
    disabled: bool = False                  # 是否禁用

    def update_on_success(self):
        """成功执行后更新统计"""
        self.success_count += 1
        self.last_used = time.time()
        # 置信度提升，但不超过 1.0
        self.confidence = min(1.0, self.confidence + 0.05)

    def update_on_failure(self):
        """失败执行后更新统计"""
        self.failure_count += 1
        self.last_used = time.time()
        # 置信度下降
        self.confidence = max(0.0, self.confidence - 0.15)
        # 置信度过低时禁用
        if self.confidence < 0.2:
            self.disabled = True

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于 YAML 序列化）"""
        return {
            "cache_id": self.cache_id,
            "agent_id": self.agent_id,
            "user_id": self.user_id,
            "task_description": self.task_description,
            "intent_pattern": self.intent_pattern,
            "trigger_keywords": self.trigger_keywords,
            "plan": self.plan,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "confidence": self.confidence,
            "created_at": self.created_at,
            "last_used": self.last_used,
            "disabled": self.disabled
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentPlanCache":
        """从字典创建实例"""
        return cls(
            cache_id=data.get("cache_id", str(uuid.uuid4())),
            agent_id=data.get("agent_id", ""),
            user_id=data.get("user_id", ""),
            task_description=data.get("task_description", ""),
            intent_pattern=data.get("intent_pattern", ""),
            trigger_keywords=data.get("trigger_keywords", []),
            plan=data.get("plan", []),
            success_count=data.get("success_count", 0),
            failure_count=data.get("failure_count", 0),
            confidence=data.get("confidence", 0.5),
            created_at=data.get("created_at", time.time()),
            last_used=data.get("last_used", time.time()),
            disabled=data.get("disabled", False)
        )
