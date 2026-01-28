# 任务执行路径保存与记忆复用方案 V2

## 1. 系统递归结构理解

```
TaskRouter
    └── AgentActor (root: marketing)
            │
            ├── _plan_task_execution() → 生成 Plan（基于自己的子节点）
            │
            └── TaskGroupAggregatorActor
                    │
                    ├── Step 1: MCP → MCPActor → 执行工具
                    │
                    └── Step 2: AGENT → ResultAggregatorActor
                                        │
                                        └── AgentActor (child: user_strat_fission)
                                                │
                                                ├── _plan_task_execution() → 生成自己的 Plan
                                                │
                                                └── TaskGroupAggregatorActor
                                                        │
                                                        ├── Step 1: MCP → ...
                                                        └── Step 2: AGENT → LeafActor
                                                                            │
                                                                            └── ExecutionActor → Dify/HTTP
```

**关键洞察**：
1. **每个 AgentActor 独立规划**：基于自己的子节点（children）生成 Plan
2. **递归嵌套**：AgentActor → TaskGroupAggregator → ResultAggregator → AgentActor（子）
3. **Plan 是局部的**：每个 Agent 只知道自己下一层的能力，不知道更深层

## 2. 问题重新定义

### 2.1 原方案问题
- 试图在 TaskRouter 层保存"完整执行路径"
- 忽略了每个 AgentActor 独立规划的事实
- 无法处理递归嵌套的 Plan

### 2.2 正确的保存粒度

| 层级 | 保存内容 | 复用场景 |
|------|----------|----------|
| **AgentActor** | 该 Agent 的局部 Plan | 相同 Agent 处理相似任务时 |
| **LeafActor** | 执行配置（参数映射） | 相同叶子节点执行相似任务时 |

## 3. 修正后的设计

### 3.1 核心概念：AgentPlanCache

```python
@dataclass
class AgentPlanCache:
    """单个 Agent 的规划缓存"""
    cache_id: str
    agent_id: str                   # 所属 Agent
    user_id: str                    # 所属用户

    # 触发条件
    intent_pattern: str             # 意图模式（正则）
    trigger_keywords: List[str]     # 触发关键词
    input_embedding: np.ndarray     # 输入的 embedding（用于语义匹配）

    # 规划结果（局部 Plan）
    plan: List[Dict[str, Any]]      # 该 Agent 生成的 Plan
    # 示例：
    # [
    #   {"step": 1, "type": "MCP", "executor": "get_user_profile", ...},
    #   {"step": 2, "type": "AGENT", "executor": "user_strat_fission", ...}
    # ]

    # 元数据
    success_count: int = 0
    failure_count: int = 0
    confidence: float = 0.5
    last_used: float = 0
    created_at: float = 0
```

### 3.2 存储结构

```
execution_cache/
├── agent_plans/                    # Agent 规划缓存
│   ├── marketing/                  # 按 agent_id 分目录
│   │   ├── user_123_fission.yaml
│   │   └── user_123_promotion.yaml
│   └── user_strat_fission/
│       └── user_123_create_task.yaml
│
└── leaf_configs/                   # 叶子节点执行配置
    └── create_fission_task/
        └── user_123_default.yaml
```

### 3.3 YAML 格式示例

```yaml
# execution_cache/agent_plans/marketing/user_123_fission.yaml
cache_id: "marketing_fission_001"
agent_id: "marketing"
user_id: "user_123"

intent_pattern: "创建.*裂变.*任务"
trigger_keywords:
  - "裂变"
  - "拉新"
  - "邀请"

plan:
  - step: 1
    type: "MCP"
    executor: "get_user_profile"
    description: "获取用户画像"
  - step: 2
    type: "AGENT"
    executor: "user_strat_fission"
    description: "执行裂变任务创建"

success_count: 5
failure_count: 0
confidence: 0.9
```

## 4. 集成点（修正）

### 4.1 AgentActor 集成

```python
# agent_actor.py

class AgentActor(Actor):
    def __init__(self):
        # ...
        self._plan_cache: Optional[AgentPlanCacheStore] = None

    def _plan_task_execution(self, task_description: str, memory_context: str = None) -> List[Dict]:
        """
        ⑤ 任务规划 - 优先查找缓存
        """
        # === 新增：查找规划缓存 ===
        if self._plan_cache is None:
            self._plan_cache = get_agent_plan_cache()

        cached_plan = self._plan_cache.find_matching_plan(
            agent_id=self.agent_id,
            user_id=self.current_user_id,
            task_description=task_description
        )

        if cached_plan and cached_plan.confidence > 0.7:
            self.log.info(f"Using cached plan for {self.agent_id}: {cached_plan.cache_id}")
            # 标记使用了缓存（用于后续统计）
            self._used_cached_plan = cached_plan.cache_id
            return cached_plan.plan

        # 正常规划流程
        subtasks = self.task_planner.generate_execution_plan(
            self.agent_id, task_description, memory_context
        )

        # === 新增：保存新规划（异步，不阻塞） ===
        self._save_plan_to_cache(task_description, subtasks)

        return subtasks

    def _handle_task_result(self, msg: TaskCompletedMessage, sender: ActorAddress):
        """处理任务完成结果"""
        # ... 原有逻辑 ...

        # === 新增：更新缓存统计 ===
        if hasattr(self, '_used_cached_plan') and self._used_cached_plan:
            if msg.status == "SUCCESS":
                self._plan_cache.update_stats(self._used_cached_plan, success=True)
            else:
                self._plan_cache.update_stats(self._used_cached_plan, success=False)
            self._used_cached_plan = None
```

### 4.2 不需要修改 TaskRouter

因为规划是在每个 AgentActor 内部进行的，TaskRouter 只负责路由，不需要知道规划缓存。

### 4.3 LeafActor 集成（可选）

```python
# leaf_actor.py

class LeafActor(Actor):
    def _handle_task(self, task: AgentTaskMessage, sender: ActorAddress):
        # ...

        # === 新增：查找执行配置缓存 ===
        cached_config = self._find_cached_execution_config(
            agent_id=self.agent_id,
            user_id=task.user_id,
            task_description=task.description
        )

        if cached_config:
            # 使用缓存的参数映射
            running_config = self._apply_cached_config(cached_config, task)
        else:
            # 正常构建 running_config
            running_config = self._build_running_config(task)

        # 发送给 ExecutionActor
        # ...
```

## 5. 与 ProceduralMemory 的协同（修正）

```
用户输入: "帮我创建一个裂变任务"
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ AgentActor (marketing)                                          │
│                                                                 │
│ Step 1: AgentPlanCache.find_matching_plan()                     │
│         → 找到缓存的 Plan？                                      │
│         → YES: 直接使用，跳过 LLM 规划                           │
│         → NO: 继续 Step 2                                       │
│                                                                 │
│ Step 2: ProceduralMemory.search()                               │
│         → 找到相关的操作步骤？                                   │
│         → 作为规划参考，注入到 Planner prompt                    │
│                                                                 │
│ Step 3: TaskPlanner.generate_execution_plan()                   │
│         → 生成新的 Plan                                         │
│         → 执行成功后保存到 AgentPlanCache                        │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ TaskGroupAggregatorActor                                        │
│ → 执行 Plan 中的每个 Step                                       │
└─────────────────────────────────────────────────────────────────┘
                    │
          ┌────────┴────────┐
          │                 │
    Step 1: MCP       Step 2: AGENT
          │                 │
          ▼                 ▼
┌─────────────────┐  ┌─────────────────────────────────────────────┐
│ MCPActor        │  │ ResultAggregatorActor                       │
│ → 执行工具      │  │ → 创建子 AgentActor                         │
└─────────────────┘  └─────────────────────────────────────────────┘
                                    │
                                    ▼
                    ┌─────────────────────────────────────────────┐
                    │ AgentActor (user_strat_fission)             │
                    │                                             │
                    │ 重复上述流程：                               │
                    │ 1. 查找自己的 AgentPlanCache                │
                    │ 2. 或使用 TaskPlanner 规划                  │
                    │ 3. 执行成功后保存缓存                       │
                    └─────────────────────────────────────────────┘
```

## 6. 数据结构

### 6.1 AgentPlanCacheStore

```python
class AgentPlanCacheStore:
    """Agent 规划缓存存储"""

    def __init__(self):
        self.cache_dir = Path("execution_cache/agent_plans")
        self.model = SentenceTransformer(...)  # 复用现有模型
        self._cache: Dict[str, List[AgentPlanCache]] = {}  # agent_id -> caches
        self._embeddings: Dict[str, np.ndarray] = {}
        self._load_all_caches()

    def find_matching_plan(
        self,
        agent_id: str,
        user_id: str,
        task_description: str,
        threshold: float = 0.7
    ) -> Optional[AgentPlanCache]:
        """
        查找匹配的规划缓存

        匹配策略：
        1. 先按 agent_id 过滤
        2. 关键词匹配
        3. 语义相似度匹配
        4. 置信度过滤
        """
        pass

    def save_plan(
        self,
        agent_id: str,
        user_id: str,
        task_description: str,
        plan: List[Dict[str, Any]]
    ) -> str:
        """保存新的规划缓存"""
        pass

    def update_stats(self, cache_id: str, success: bool):
        """更新缓存统计"""
        pass
```

## 7. 实现计划（修正）

### Phase 1: 基础存储
- [ ] 定义 AgentPlanCache 数据结构
- [ ] 实现 AgentPlanCacheStore（YAML + Embedding）
- [ ] 实现 find_matching_plan / save_plan

### Phase 2: AgentActor 集成
- [ ] 在 `_plan_task_execution` 中添加缓存查找
- [ ] 在 `_handle_task_result` 中添加统计更新
- [ ] 添加异步保存逻辑

### Phase 3: 置信度管理
- [ ] 实现置信度更新逻辑
- [ ] 添加缓存过期/清理机制

### Phase 4: LeafActor 集成（可选）
- [ ] 执行配置缓存
- [ ] 参数映射复用

## 8. 文件结构（修正）

```
tasks/
├── capabilities/
│   └── plan_cache/                  # 新增模块
│       ├── __init__.py
│       ├── interface.py             # IPlanCacheCapability
│       ├── agent_plan_cache.py      # AgentPlanCache 数据结构
│       ├── plan_cache_store.py      # AgentPlanCacheStore
│       └── confidence_manager.py    # 置信度管理
│
├── execution_cache/                 # 存储目录
│   ├── agent_plans/
│   │   └── {agent_id}/
│   │       └── *.yaml
│   └── leaf_configs/
│       └── {agent_id}/
│           └── *.yaml
```

## 9. 与原方案的区别

| 方面 | 原方案 V1 | 修正方案 V2 |
|------|-----------|-------------|
| **保存粒度** | 完整执行路径 | 每个 Agent 的局部 Plan |
| **集成点** | TaskRouter | AgentActor |
| **递归支持** | ❌ 不支持 | ✅ 每层独立缓存 |
| **复杂度** | 高（需要追踪完整链路） | 低（局部缓存） |
| **复用范围** | 完全相同的任务 | 相似任务（同一 Agent） |

## 10. 总结

修正后的方案：
1. **尊重递归结构**：每个 AgentActor 独立管理自己的规划缓存
2. **局部优化**：不试图保存完整链路，而是优化每一层的规划
3. **低侵入性**：只需修改 AgentActor 的 `_plan_task_execution` 方法
4. **渐进学习**：每个 Agent 独立学习自己的最佳规划
