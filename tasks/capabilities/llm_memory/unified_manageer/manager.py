"""统一记忆管理器模块"""
from typing import Dict, Any, Optional, List
import time  # 用于测试时等待 embedding 完成
import logging

# 使用相对导入
from ...capability_base import CapabilityBase
from .short_term import ShortTermMemory

logger = logging.getLogger(__name__)

# 导入 mem0
from mem0 import Memory
from config import MEM0_CONFIG

# === 全局共享的重量级资源（只初始化一次）===
try:
    SHARED_MEM0_CLIENT = Memory.from_config(MEM0_CONFIG)
    logger.info("Mem0 client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Mem0 client: {e}")
    SHARED_MEM0_CLIENT = None  # 允许系统继续运行，后续会降级处理


from datetime import datetime
import json
import os
import re
from .memory_interfaces import IVaultRepository, IProceduralRepository, IResourceRepository

# 导入工厂函数
from external.memory_store.memory_repos import (
    build_vault_repo,
    build_procedural_repo,
    build_resource_repo
)


class UnifiedMemoryManager():
    def __init__(self,
                # user_id: str="default",
                vault_repo: IVaultRepository=None,
                procedural_repo: IProceduralRepository=None,
                resource_repo: IResourceRepository=None,
                mem0_client=None,
                qwen_client=None
                ):
        # self.user_id = user_id
        self.mem0 = mem0_client or SHARED_MEM0_CLIENT
        self.stm = ShortTermMemory(max_history=10)  # 仍保留短期对话历史
        self.qwen = qwen_client # ← 关键！
        # 各专用存储（使用工厂函数，lazy init）
        try:
            self.vault_repo = vault_repo or build_vault_repo()
        except Exception as e:
            logger.warning(f"Failed to initialize vault_repo: {e}")
            self.vault_repo = None
        try:
            self.procedural_repo = procedural_repo or build_procedural_repo()
        except Exception as e:
            logger.warning(f"Failed to initialize procedural_repo: {e}")
            self.procedural_repo = None
        try:
            self.resource_repo = resource_repo or build_resource_repo()
        except Exception as e:
            logger.warning(f"Failed to initialize resource_repo: {e}")
            self.resource_repo = None
        self._core_cache = None

    # ======================
    # 1. 六类记忆写入接口
    # ======================

    def add_memory_intelligently(self,user_id,content: str, metadata: Dict = None):
        """
        智能记忆路由：
        1. 先存入短期记忆
        2. 调用 Qwen 分析并拆解为多类长期记忆
        3. 分别写入对应存储
        """
        logger.info(f"🔍 [ADD] USER={user_id} | CONTENT='{content[:100]}...'")

        # Step 1: 存入短期记忆（原始内容）- 这个必须成功
        try:
            self.stm.add_message(content=content, role="user", user_id=user_id)
        except Exception as e:
            logger.error(f"Failed to add to short-term memory: {e}")

        # 检查 Mem0 是否可用
        if self.mem0 is None:
            logger.warning("Mem0 client not available, skipping long-term memory storage")
            return

        # 初始化 Qwen 客户端
        if self.qwen is None:
            try:
                from ...registry import capability_registry
                from ...llm.interface import ILLMCapability
                self.qwen = capability_registry.get_capability(
                    "llm", expected_type=ILLMCapability
                )
            except Exception as e:
                logger.warning(f"LLM capability not available: {e}, using fallback to episodic")
                self._fallback_add_episodic(user_id, content)
                return

        # Step 2: 调用 Qwen 分类
        prompt = self._build_memory_classification_prompt(content)
        try:
            response = self.qwen.generate(
                prompt=prompt,
                max_tokens=512,
                temperature=0.1,  # 降低随机性
                stop=["\n\n"]  # 可选
            )
            parsed = json.loads(response.strip())
        except Exception as e:
            logger.warning(f"[MemoryRouter] Qwen 解析失败: {e}，回退为 episodic")
            self._fallback_add_episodic(user_id, content)
            return

        # Step 3: 按类别写入
        if "core" in parsed:
            for item in parsed["core"]:
                self.add_core_memory(user_id,item.strip())

        if "episodic" in parsed:
            for item in parsed["episodic"]:
                self.add_episodic_memory(user_id,item.strip())

        if "semantic" in parsed:
            for item in parsed["semantic"]:
                self.add_semantic_memory(user_id,item.strip())

        if "procedural" in parsed and self.procedural_repo:
            for item in parsed["procedural"]:
                # 简化：将整句作为单步流程；进阶可让 Qwen 拆 steps
                self.add_procedural_memory(
                    user_id=user_id,
                    domain="general",
                    task_type="user_defined",
                    title=item[:50],  # 截取标题
                    steps=[item.strip()]
                )

        if "resource" in parsed and self.resource_repo:
            for item in parsed["resource"]:
                # 进阶：可用正则提取路径，这里简化处理
                self.add_resource_memory(
                    user_id=user_id,
                    file_path="mentioned_in_text",
                    summary=item.strip(),
                    doc_type="text"
                )

        if "vault" in parsed and self.vault_repo:
            for item in parsed["vault"]:
                # ⚠️ 安全建议：不要直接存储明文！这里仅为演示
                self.add_vault_memory(
                    user_id=user_id,
                    category="sensitive_auto_detected",
                    key_name="auto_" + str(hash(item))[:8],
                    value=item.strip()
                )

    def _fallback_add_episodic(self, user_id: str, content: str):
        """降级方案：直接存入情景记忆"""
        try:
            if self.mem0:
                self.add_episodic_memory(user_id, content)
        except Exception as e:
            logger.error(f"Fallback episodic memory also failed: {e}")


    def _build_memory_classification_prompt(self, user_input: str) -> str:
        return f"""
    你是一个高级记忆管理系统，负责将用户的自然语言输入智能拆解为多个记忆片段，并分类存储到以下六类长期记忆中：

    - **core**: 用户身份、偏好、长期属性（如“我是设计师”、“我不吃香菜”）
    - **episodic**: 具体事件，含时间/地点/人物（如“昨天我去了上海开会”）
    - **semantic**: 通用知识、事实、概念（如“光速是 3×10^8 m/s”）
    - **procedural**: 操作步骤、方法、流程（如“重装系统要先备份数据”）
    - **resource**: 提到的文件、链接、文档（如“见附件 resume.pdf”）
    - **vault**: 敏感信息（密码、token、身份证等，需谨慎处理）

    请严格按以下 JSON 格式输出，仅包含存在的类别，每个类别对应一个**字符串列表**（可多条）：

    {{
    "core": ["..."],
    "episodic": ["..."],
    "semantic": ["..."],
    "procedural": ["..."],
    "resource": ["..."],
    "vault": ["..."]
    }}

    注意：
    - 不要编造内容，只提取用户明确提到的信息。
    - 同一句话的不同部分可归属不同类别。
    - 若某类别无内容，则省略该字段。
    - 不要输出任何其他文字，只输出 JSON。

    用户输入：
    {user_input}
    """


    def add_core_memory(self, user_id,content: str):
        """核心记忆：用户基本信息、偏好"""
        if not self.mem0:
            logger.warning("Mem0 not available, skipping core memory")
            return
        try:
            self.mem0.add(
                content,
                user_id=user_id,
                metadata={"type": "core", "updated_at": datetime.now().isoformat()}
            )
            self._core_cache = None  # 失效缓存
        except Exception as e:
            logger.error(f"Failed to add core memory: {e}")

    def add_episodic_memory(self, user_id,content: str, timestamp: str = None):
        """情景记忆：具体事件"""
        if not self.mem0:
            logger.warning("Mem0 not available, skipping episodic memory")
            return
        try:
            meta = {
                "type": "episodic",
                "timestamp": timestamp or datetime.now().isoformat()
            }
            self.mem0.add(content, user_id=user_id, metadata=meta)
        except Exception as e:
            logger.error(f"Failed to add episodic memory: {e}")

    def add_vault_memory(self,user_id, category: str, key_name: str, value: str):
        if not self.vault_repo:
            logger.warning("Vault repo not available, skipping vault memory")
            return
        try:
            self.vault_repo.store(user_id, category, key_name, value)
        except Exception as e:
            logger.error(f"Failed to add vault memory: {e}")

    def add_procedural_memory(self, user_id: str, domain: str, task_type: str, title: str, steps: List[str]):
        if not self.procedural_repo:
            logger.warning("Procedural repo not available, skipping procedural memory")
            return
        try:
            self.procedural_repo.add_procedure(user_id, domain, task_type, title, steps)
        except Exception as e:
            logger.error(f"Failed to add procedural memory: {e}")

    def add_resource_memory(self, user_id: str, file_path: str, summary: str, doc_type: str = "pdf"):
        if not self.resource_repo:
            logger.warning("Resource repo not available, skipping resource memory")
            return
        try:
            self.resource_repo.add_document(user_id, file_path, summary, doc_type)
        except Exception as e:
            logger.error(f"Failed to add resource memory: {e}")

    def add_semantic_memory(self, user_id: str, content: str, category: str = ""):
        """语义记忆：事实性知识"""
        if not self.mem0:
            logger.warning("Mem0 not available, skipping semantic memory")
            return
        try:
            meta = {"type": "semantic"}
            if category: meta["category"] = category
            self.mem0.add(content, user_id=user_id, metadata=meta)
        except Exception as e:
            logger.error(f"Failed to add semantic memory: {e}")

    # ======================
    # 2. 记忆检索接口（按类型）
    # ======================

    def _search_by_type(self, user_id: str, memory_type: str, query: str = "", limit: int = 5):
        if not self.mem0:
            logger.warning("Mem0 not available for search")
            return []
        try:
            filters = {"type": memory_type}
            if not query:
                query = "relevant information"  # Mem0 要求 query 非空
            results = self.mem0.search(
                user_id=user_id,
                query=query,
                filters=filters,
                limit=limit
            )
            return [r.get("memory", "") for r in results.get("results", [])]
        except Exception as e:
            logger.error(f"Failed to search memory by type {memory_type}: {e}")
            return []

    def get_core_memory(self, user_id: str) -> str:
        """获取核心记忆（缓存优化）"""
        logger.debug(f"Retrieving core memory for user {user_id}")
        if self._core_cache is None:
            logger.debug(f"Cache miss for core memory, fetching from Mem0 for user {user_id}")
            memories = self._search_by_type(user_id, "core", limit=10)
            self._core_cache = "\n".join(memories) if memories else ""
        return self._core_cache

    def get_episodic_memory(self, user_id: str, query: str, limit: int = 3) -> str:
        return "\n".join(self._search_by_type(user_id, "episodic", query, limit))

    # 修改检索方法
    def get_vault_memory(self, user_id: str, category: str = None) -> str:
        if not self.vault_repo:
            logger.warning("Vault repo not available for retrieval")
            return ""
        try:
            items = self.vault_repo.retrieve(user_id, category)
            return "\n".join(items) if items else ""
        except Exception as e:
            logger.error(f"Failed to retrieve vault memory: {e}")
            return ""

    def get_procedural_memory(self, user_id: str, query: str, domain: str = None, limit: int = 2) -> str:
        if not self.procedural_repo:
            logger.warning("Procedural repo not available for retrieval")
            return ""
        try:
            results = self.procedural_repo.search(user_id, query, domain=domain, limit=limit)
            return "\n\n".join(results) if results else ""
        except Exception as e:
            logger.error(f"Failed to retrieve procedural memory: {e}")
            return ""

    def get_resource_memory(self, user_id: str, query: str) -> str:
        if not self.resource_repo:
            logger.warning("Resource repo not available for retrieval")
            return ""
        try:
            docs = self.resource_repo.search(user_id, query, limit=2)
            if not docs:
                return ""
            return "\n".join([
                f"[{d['filename']}]: {d['summary']} (ID: {d['id']})"
                for d in docs
            ])
        except Exception as e:
            logger.error(f"Failed to retrieve resource memory: {e}")
            return ""
    # ======================
    # 3. 上下文构建（供 LLM 使用）
    # ======================

    def _generate_retrieval_plan(self, goal: str, scene: str) -> Dict[str, str]:
        """使用 Qwen 动态生成多类型记忆的检索查询"""
        prompt = f"""你是一个高级记忆系统调度器。请根据以下场景和目标，为六类记忆生成最相关的检索关键词或短句。
    仅输出 JSON，包含需要检索的类别及其查询语句。不要解释，不要多余字段。

    场景：{scene}
    目标：{goal}

    输出格式示例：
    {{"core": "用户姓名和职业偏好", "episodic": "最近一次出差或项目经历"}}

    你的输出：
    """
        try:
            resp = self.qwen.generate(prompt, max_tokens=256, temperature=0.1)
            return json.loads(resp.strip())
        except Exception as e:
            # fallback plan
            return {
                "core": goal,
                "episodic": goal,
                "semantic": goal,
                "procedural": goal,
                "resource": goal
            }

    def _execute_retrieval_plan(self, user_id: str, plan: Dict[str, str]) -> Dict[str, str]:
        """执行检索计划，返回原始记忆片段字典"""
        results = {}

        if "core" in plan:
            core = self.get_core_memory(user_id)
            if core:
                results["core"] = core

        if "episodic" in plan:
            episodic = self.get_episodic_memory(user_id, plan["episodic"], limit=3)
            if episodic:
                results["episodic"] = episodic

        if "semantic" in plan:
            semantic = "\n".join(self._search_by_type(user_id, "semantic", plan["semantic"], limit=3))
            if semantic:
                results["semantic"] = semantic

        if "procedural" in plan:
            procedural = self.get_procedural_memory(user_id, plan["procedural"], domain=None, limit=3)
            if procedural:
                results["procedural"] = procedural

        if "resource" in plan:
            resource = self.get_resource_memory(user_id, plan["resource"])
            if resource:
                results["resource"] = resource

        # vault 不在此处自动检索（安全原因），由 build_execution_context 显式控制

        return results

    def _synthesize_context_with_qwen(self, user_id: str, raw_memories: Dict[str, str], scene: str, include_vault: bool = False) -> str:
        """使用 Qwen 合成最终上下文，自动脱敏"""
        # 获取 vault（仅当显式允许）
        if include_vault:
            vault = self.get_vault_memory(user_id)
            if vault:
                # 简单脱敏：替换 token / 密码等（可扩展正则）
                vault = re.sub(r'(?i)(token|password|key|secret)[:\s]*[\'"]?[\w\-_\.]+[\'"]?', r'\1: [REDACTED]', vault)
                raw_memories["vault"] = vault

        if not raw_memories:
            return "无相关记忆可用。"

        memory_blocks = "\n\n".join(f"[{k.upper()} MEMORY]\n{v}" for k, v in raw_memories.items())

        prompt = f"""你是一个 AI 助手的记忆整合模块。请将以下记忆片段整合成一段简洁、连贯、适合用于「{scene}」的上下文描述。

    要求：
    - 保留所有关键事实（如姓名、时间、文件名、操作步骤）
    - 合并重复或相似内容
    - 使用自然语言，避免标签如 [CORE MEMORY]
    - 敏感信息必须显示为 [REDACTED]
    - 不要编造未提及的信息
    - 输出纯文本，不要 Markdown

    记忆内容：
    {memory_blocks}

    整合后的上下文：
    """
        try:
            synthesized = self.qwen.generate(prompt, max_tokens=512, temperature=0.3)
            return synthesized.strip()
        except Exception as e:
            # fallback: 直接拼接（不合成）
            return "\n\n".join(raw_memories.values())


    # ======================
    # 3. 智能上下文构建（按场景，Qwen 全程驱动）
    # ======================

    def build_conversation_context(self, user_id: str, current_input: str = "") -> str:
        """
        场景1：对话理解 & 任务选择
        - Qwen 动态决定查哪些记忆
        - 合成自然语言上下文供 LLM 理解用户意图
        """
        goal = current_input or "当前对话上下文"
        plan = self._generate_retrieval_plan(goal, scene="对话理解与任务选择")
        raw = self._execute_retrieval_plan(user_id, plan)
        
        
        chat_hist = ""
        if user_id and user_id.count(":") == 1:
            chat_hist = self.stm.format_history_by_scope(user_id, n=6)
        else:
            chat_hist = self.stm.format_history(user_id,n=6)
        if chat_hist.strip():
            raw["short_term"] = f"[近期对话]\n{chat_hist}"

        return self._synthesize_context_with_qwen(user_id, raw, scene="对话理解")


    def build_planning_context(self, user_id: str, planning_goal: str) -> str:
        """
        场景2：任务规划与流程编排
        - 重点获取 procedural、episodic、resource
        - 合成后用于任务分解与排序
        """
        plan = self._generate_retrieval_plan(planning_goal, scene="多任务规划与调度")
        raw = self._execute_retrieval_plan(user_id, plan)
        return self._synthesize_context_with_qwen(user_id, raw, scene="任务规划")


    def build_execution_context(self, user_id: str, task_description: str, include_sensitive: bool = False) -> str:
        """
        场景3：任务执行前增强
        - 补充历史经验、标准流程、参考资料
        - 可选包含 vault（自动脱敏）
        """
        plan = self._generate_retrieval_plan(task_description, scene="具体任务执行准备")
        raw = self._execute_retrieval_plan(user_id, plan)
        return self._synthesize_context_with_qwen(
            user_id,
            raw, 
            scene="任务执行", 
            include_vault=include_sensitive
        )

# ======================
    # 4. 语义指针补全：父级记忆回溯
    # ======================

    def get_ancestor_context(
        self,
        user_id: str,
        agent_id: str,
        tree_manager: Any,
        max_levels: int = 3,
        query: str = ""
    ) -> List[Dict[str, Any]]:
        """
        沿树向上回溯，收集父级 Agent 的业务记忆，用于消解代词歧义。

        机制：
        - 从当前 agent_id 开始，沿树向上遍历父级 Agent
        - 检索每级的对话历史和核心记忆
        - 返回按层级排序的上下文列表（近到远）

        Args:
            user_id: 用户ID
            agent_id: 当前 Agent ID
            tree_manager: TreeManager 实例，用于获取父级关系
            max_levels: 最大回溯层数，默认 3 层
            query: 可选的查询关键词，用于相关性过滤

        Returns:
            List[Dict]: 每级父节点的上下文信息
            [
                {
                    "agent_id": "parent_agent_1",
                    "level": 1,
                    "conversation_history": "...",
                    "core_memory": "...",
                    "agent_description": "...",
                    "task_goal": "..."
                },
                ...
            ]
        """
        if not tree_manager:
            return []

        ancestor_contexts = []
        current_id = agent_id
        level = 0

        while level < max_levels:
            # 获取父节点
            parent_id = tree_manager.get_parent(current_id)
            if not parent_id:
                break  # 已到达根节点

            level += 1

            # 构建父节点的记忆 scope
            # 格式: user_id:root_agent_id:parent_agent_id
            root_path = tree_manager.get_full_path(parent_id)
            root_agent_id = root_path[0] if root_path else parent_id
            parent_scope = f"{user_id}:{root_agent_id}:{parent_id}"

            # 获取父节点的对话历史
            conversation_history = ""
            try:
                conversation_history = self.stm.format_history_by_scope(parent_scope, n=5)
                if not conversation_history:
                    # 尝试更宽松的 scope
                    broader_scope = f"{user_id}:{root_agent_id}"
                    conversation_history = self.stm.format_history_by_scope(broader_scope, n=5)
            except Exception as e:
                print(f"[AncestorContext] Failed to get conversation history for {parent_id}: {e}")

            # 获取父节点的核心记忆
            core_memory = ""
            try:
                core_memory = self.get_core_memory(user_id)
            except Exception as e:
                print(f"[AncestorContext] Failed to get core memory for {parent_id}: {e}")

            # 获取父节点的元数据（描述、任务目标等）
            agent_description = ""
            task_goal = ""
            try:
                parent_meta = tree_manager.get_agent_meta(parent_id)
                if parent_meta:
                    agent_description = parent_meta.get("description", "")
                    # 尝试从 datascope 或 capability 中提取任务目标
                    datascope = parent_meta.get("datascope") or parent_meta.get("data_scope", "")
                    capability = parent_meta.get("capability", "")
                    if datascope:
                        task_goal = f"数据范围: {datascope}"
                    if capability:
                        task_goal += f" 能力: {capability}"
            except Exception as e:
                print(f"[AncestorContext] Failed to get agent meta for {parent_id}: {e}")

            # 如果有查询关键词，进行相关性过滤
            if query:
                # 简单的关键词匹配过滤
                combined_text = f"{conversation_history} {core_memory} {agent_description} {task_goal}"
                query_keywords = set(query.lower().split())
                combined_lower = combined_text.lower()
                relevance_score = sum(1 for kw in query_keywords if kw in combined_lower)

                # 如果完全不相关，跳过这一层
                if relevance_score == 0 and level > 1:
                    current_id = parent_id
                    continue

            ancestor_context = {
                "agent_id": parent_id,
                "level": level,
                "conversation_history": conversation_history,
                "core_memory": core_memory,
                "agent_description": agent_description,
                "task_goal": task_goal
            }

            ancestor_contexts.append(ancestor_context)
            current_id = parent_id

        return ancestor_contexts

    def build_ancestor_context_summary(
        self,
        user_id: str,
        agent_id: str,
        tree_manager: Any,
        max_levels: int = 3,
        query: str = ""
    ) -> str:
        """
        构建父级上下文的摘要文本，用于注入到 LLM prompt 中。

        Args:
            user_id: 用户ID
            agent_id: 当前 Agent ID
            tree_manager: TreeManager 实例
            max_levels: 最大回溯层数
            query: 可选的查询关键词

        Returns:
            str: 格式化的父级上下文摘要
        """
        ancestors = self.get_ancestor_context(
            user_id=user_id,
            agent_id=agent_id,
            tree_manager=tree_manager,
            max_levels=max_levels,
            query=query
        )

        if not ancestors:
            return ""

        summary_parts = []
        for ctx in ancestors:
            level = ctx["level"]
            agent_id = ctx["agent_id"]

            parts = [f"【父级 {level} - {agent_id}】"]

            if ctx.get("agent_description"):
                parts.append(f"描述: {ctx['agent_description']}")

            if ctx.get("task_goal"):
                parts.append(f"任务目标: {ctx['task_goal']}")

            if ctx.get("conversation_history"):
                # 截取最近的对话，避免过长
                history = ctx["conversation_history"]
                if len(history) > 500:
                    history = history[-500:] + "..."
                parts.append(f"近期对话:\n{history}")

            if ctx.get("core_memory"):
                memory = ctx["core_memory"]
                if len(memory) > 300:
                    memory = memory[:300] + "..."
                parts.append(f"核心记忆: {memory}")

            summary_parts.append("\n".join(parts))

        return "\n\n".join(summary_parts)
