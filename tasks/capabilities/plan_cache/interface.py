# interface.py
"""规划缓存能力接口"""

from abc import abstractmethod
from typing import List, Dict, Any, Optional

from ..capability_base import CapabilityBase
from .agent_plan_cache import AgentPlanCache


class IPlanCacheCapability(CapabilityBase):
    """规划缓存能力接口"""

    @abstractmethod
    def find_matching_plan(
        self,
        agent_id: str,
        user_id: str,
        task_description: str,
        threshold: float = 0.7
    ) -> Optional[AgentPlanCache]:
        """
        查找匹配的规划缓存

        Args:
            agent_id: Agent ID
            user_id: 用户 ID
            task_description: 任务描述
            threshold: 相似度阈值

        Returns:
            匹配的缓存，如果没有则返回 None
        """
        pass

    @abstractmethod
    def save_plan(
        self,
        agent_id: str,
        user_id: str,
        task_description: str,
        plan: List[Dict[str, Any]],
        trigger_keywords: List[str] = None
    ) -> str:
        """
        保存规划缓存

        Args:
            agent_id: Agent ID
            user_id: 用户 ID
            task_description: 任务描述
            plan: 规划结果
            trigger_keywords: 触发关键词（可选）

        Returns:
            缓存 ID
        """
        pass

    @abstractmethod
    def update_stats(self, cache_id: str, success: bool) -> bool:
        """
        更新缓存统计

        Args:
            cache_id: 缓存 ID
            success: 是否成功

        Returns:
            是否更新成功
        """
        pass

    @abstractmethod
    def get_cache_by_id(self, cache_id: str) -> Optional[AgentPlanCache]:
        """
        根据 ID 获取缓存

        Args:
            cache_id: 缓存 ID

        Returns:
            缓存对象
        """
        pass

    @abstractmethod
    def list_caches(
        self,
        agent_id: str = None,
        user_id: str = None,
        include_disabled: bool = False
    ) -> List[AgentPlanCache]:
        """
        列出缓存

        Args:
            agent_id: 按 Agent ID 过滤
            user_id: 按用户 ID 过滤
            include_disabled: 是否包含已禁用的缓存

        Returns:
            缓存列表
        """
        pass

    @abstractmethod
    def delete_cache(self, cache_id: str) -> bool:
        """
        删除缓存

        Args:
            cache_id: 缓存 ID

        Returns:
            是否删除成功
        """
        pass

    def get_capability_type(self) -> str:
        return "plan_cache"
