# plan_cache_store.py
"""规划缓存存储实现"""

import os
import re
import yaml
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np

from .interface import IPlanCacheCapability
from .agent_plan_cache import AgentPlanCache

logger = logging.getLogger(__name__)

# 默认缓存目录
DEFAULT_CACHE_DIR = "execution_cache/agent_plans"


class PlanCacheStore(IPlanCacheCapability):
    """
    规划缓存存储

    使用 YAML 文件 + Embedding 实现规划缓存的存储和检索。
    按 agent_id 分目录存储，支持语义相似度匹配。
    """

    def __init__(self, cache_dir: str = None, model_name: str = "all-MiniLM-L6-v2"):
        """
        初始化缓存存储

        Args:
            cache_dir: 缓存目录路径
            model_name: Embedding 模型名称
        """
        self.cache_dir = Path(cache_dir or DEFAULT_CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 内存缓存: agent_id -> List[AgentPlanCache]
        self._caches: Dict[str, List[AgentPlanCache]] = {}
        # Embedding 缓存: cache_id -> embedding
        self._embeddings: Dict[str, np.ndarray] = {}

        # 延迟加载 embedding 模型
        self._model = None
        self._model_name = model_name

        # 加载所有缓存
        self._load_all_caches()

    def _get_model(self):
        """延迟加载 embedding 模型"""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                # 使用本地 ONNX 模型
                local_model_path = os.environ.get(
                    "EMBEDDING_MODEL_PATH",
                    str(Path(__file__).parent.parent.parent.parent / "all-MiniLM-L6-v2(1)" / "onnx")
                )
                if Path(local_model_path).exists():
                    self._model = SentenceTransformer(
                        local_model_path,
                        backend="onnx",
                        local_files_only=True
                    )
                else:
                    self._model = SentenceTransformer(self._model_name)
                logger.info(f"Loaded embedding model from {local_model_path}")
            except Exception as e:
                logger.warning(f"Failed to load embedding model: {e}, using keyword matching only")
                self._model = None
        return self._model

    def _load_all_caches(self):
        """从磁盘加载所有缓存"""
        self._caches = {}
        self._embeddings = {}

        if not self.cache_dir.exists():
            return

        # 遍历 agent_id 目录
        for agent_dir in self.cache_dir.iterdir():
            if not agent_dir.is_dir():
                continue

            agent_id = agent_dir.name
            self._caches[agent_id] = []

            # 加载该 agent 的所有缓存文件
            for cache_file in agent_dir.glob("*.yaml"):
                try:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                        if data:
                            cache = AgentPlanCache.from_dict(data)
                            self._caches[agent_id].append(cache)
                            # 计算 embedding
                            self._compute_embedding(cache)
                except Exception as e:
                    logger.warning(f"Failed to load cache file {cache_file}: {e}")

        total = sum(len(caches) for caches in self._caches.values())
        logger.info(f"Loaded {total} plan caches from {self.cache_dir}")

    def _compute_embedding(self, cache: AgentPlanCache):
        """计算缓存的 embedding"""
        model = self._get_model()
        if model is None:
            return

        try:
            # 使用任务描述 + 关键词作为 embedding 输入
            text = cache.task_description
            if cache.trigger_keywords:
                text += " " + " ".join(cache.trigger_keywords)
            embedding = model.encode([text])[0]
            self._embeddings[cache.cache_id] = embedding
        except Exception as e:
            logger.warning(f"Failed to compute embedding for cache {cache.cache_id}: {e}")

    def _get_cache_file_path(self, agent_id: str, cache_id: str) -> Path:
        """获取缓存文件路径"""
        agent_dir = self.cache_dir / agent_id
        agent_dir.mkdir(parents=True, exist_ok=True)
        # 使用 cache_id 的前 8 位作为文件名
        filename = f"{cache_id[:8]}.yaml"
        return agent_dir / filename

    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        # 简单实现：提取中文词和英文词
        # 可以后续替换为更复杂的关键词提取算法
        keywords = []

        # 提取中文词（2-4 字）
        chinese_pattern = r'[\u4e00-\u9fa5]{2,4}'
        chinese_words = re.findall(chinese_pattern, text)
        keywords.extend(chinese_words)

        # 提取英文词
        english_pattern = r'[a-zA-Z_]{3,}'
        english_words = re.findall(english_pattern, text)
        keywords.extend([w.lower() for w in english_words])

        # 去重并限制数量
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)
        return unique_keywords[:10]

    def find_matching_plan(
        self,
        agent_id: str,
        user_id: str,
        task_description: str,
        threshold: float = 0.7
    ) -> Optional[AgentPlanCache]:
        """查找匹配的规划缓存"""
        if agent_id not in self._caches:
            return None

        candidates = self._caches[agent_id]
        if not candidates:
            return None

        # 过滤：只考虑未禁用的、置信度足够的缓存
        valid_caches = [
            c for c in candidates
            if not c.disabled and c.confidence >= 0.3
        ]

        if not valid_caches:
            return None

        best_match = None
        best_score = 0.0

        # 1. 尝试语义相似度匹配
        model = self._get_model()
        if model is not None:
            try:
                query_embedding = model.encode([task_description])[0]

                for cache in valid_caches:
                    if cache.cache_id not in self._embeddings:
                        continue

                    cache_embedding = self._embeddings[cache.cache_id]
                    # 余弦相似度
                    similarity = np.dot(query_embedding, cache_embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(cache_embedding) + 1e-8
                    )

                    # 用户匹配加分
                    if cache.user_id and cache.user_id == user_id:
                        similarity += 0.1

                    # 置信度加权
                    weighted_score = similarity * cache.confidence

                    if weighted_score > best_score:
                        best_score = weighted_score
                        best_match = cache

            except Exception as e:
                logger.warning(f"Embedding matching failed: {e}, falling back to keyword matching")

        # 2. 如果语义匹配分数不够，尝试关键词匹配
        if best_score < threshold:
            task_keywords = set(self._extract_keywords(task_description))

            for cache in valid_caches:
                if not cache.trigger_keywords:
                    continue

                cache_keywords = set(cache.trigger_keywords)
                # 计算关键词重叠度
                overlap = len(task_keywords & cache_keywords)
                if overlap == 0:
                    continue

                keyword_score = overlap / max(len(task_keywords), len(cache_keywords))

                # 用户匹配加分
                if cache.user_id and cache.user_id == user_id:
                    keyword_score += 0.1

                # 置信度加权
                weighted_score = keyword_score * cache.confidence

                if weighted_score > best_score:
                    best_score = weighted_score
                    best_match = cache

        # 检查是否达到阈值
        if best_match and best_score >= threshold:
            logger.info(
                f"Found matching plan cache: {best_match.cache_id} "
                f"(score={best_score:.2f}, confidence={best_match.confidence:.2f})"
            )
            return best_match

        return None

    def save_plan(
        self,
        agent_id: str,
        user_id: str,
        task_description: str,
        plan: List[Dict[str, Any]],
        trigger_keywords: List[str] = None
    ) -> str:
        """保存规划缓存"""
        # 提取关键词
        if trigger_keywords is None:
            trigger_keywords = self._extract_keywords(task_description)

        # 创建缓存对象
        cache = AgentPlanCache(
            agent_id=agent_id,
            user_id=user_id,
            task_description=task_description,
            trigger_keywords=trigger_keywords,
            plan=plan,
            confidence=0.5  # 初始置信度
        )

        # 保存到内存
        if agent_id not in self._caches:
            self._caches[agent_id] = []
        self._caches[agent_id].append(cache)

        # 计算 embedding
        self._compute_embedding(cache)

        # 保存到磁盘
        file_path = self._get_cache_file_path(agent_id, cache.cache_id)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(cache.to_dict(), f, allow_unicode=True, indent=2)
            logger.info(f"Saved plan cache: {cache.cache_id} to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save plan cache to {file_path}: {e}")

        return cache.cache_id

    def update_stats(self, cache_id: str, success: bool) -> bool:
        """更新缓存统计"""
        cache = self.get_cache_by_id(cache_id)
        if cache is None:
            return False

        if success:
            cache.update_on_success()
        else:
            cache.update_on_failure()

        # 保存到磁盘
        file_path = self._get_cache_file_path(cache.agent_id, cache.cache_id)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(cache.to_dict(), f, allow_unicode=True, indent=2)
            logger.info(
                f"Updated cache stats: {cache_id} "
                f"(success={success}, confidence={cache.confidence:.2f})"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to update cache stats: {e}")
            return False

    def get_cache_by_id(self, cache_id: str) -> Optional[AgentPlanCache]:
        """根据 ID 获取缓存"""
        for caches in self._caches.values():
            for cache in caches:
                if cache.cache_id == cache_id:
                    return cache
        return None

    def list_caches(
        self,
        agent_id: str = None,
        user_id: str = None,
        include_disabled: bool = False
    ) -> List[AgentPlanCache]:
        """列出缓存"""
        result = []

        if agent_id:
            caches = self._caches.get(agent_id, [])
        else:
            caches = [c for caches in self._caches.values() for c in caches]

        for cache in caches:
            if not include_disabled and cache.disabled:
                continue
            if user_id and cache.user_id and cache.user_id != user_id:
                continue
            result.append(cache)

        return result

    def delete_cache(self, cache_id: str) -> bool:
        """删除缓存"""
        cache = self.get_cache_by_id(cache_id)
        if cache is None:
            return False

        # 从内存删除
        if cache.agent_id in self._caches:
            self._caches[cache.agent_id] = [
                c for c in self._caches[cache.agent_id]
                if c.cache_id != cache_id
            ]

        # 删除 embedding
        if cache_id in self._embeddings:
            del self._embeddings[cache_id]

        # 从磁盘删除
        file_path = self._get_cache_file_path(cache.agent_id, cache.cache_id)
        try:
            if file_path.exists():
                file_path.unlink()
            logger.info(f"Deleted cache: {cache_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete cache file: {e}")
            return False


# 全局单例
_SHARED_PLAN_CACHE_STORE: Optional[PlanCacheStore] = None


def get_plan_cache_store() -> PlanCacheStore:
    """获取全局规划缓存存储实例"""
    global _SHARED_PLAN_CACHE_STORE
    if _SHARED_PLAN_CACHE_STORE is None:
        _SHARED_PLAN_CACHE_STORE = PlanCacheStore()
    return _SHARED_PLAN_CACHE_STORE
