# 任务执行路径保存与记忆复用方案

## 1. 问题背景

当前系统每次执行任务都需要：
1. 意图识别 → 选择 Agent
2. 任务规划 → 生成 Plan（步骤列表）
3. 逐步执行 → 调用 MCP/Dify 等

**痛点**：
- 相似任务每次都要重新规划，浪费时间和 Token
- 成功的执行路径没有被记住，无法复用
- 用户重复执行类似任务时体验不佳

## 2. 目标

1. **执行路径保存**：任务成功完成后，保存完整的执行路径（Plan + 参数映射）
2. **路径复用**：下次执行类似任务时，直接使用已保存的路径，跳过规划阶段
3. **记忆增强**：利用现有 Procedural Memory 记住成功模式，辅助规划

## 3. 核心概念

### 3.1 ExecutionPath（执行路径）

```python
@dataclass
class ExecutionPath:
    """已验证的任务执行路径"""
    path_id: str                    # 唯一标识
    user_id: str                    # 所属用户
    agent_id: str                   # 根 Agent

    # 触发条件
    intent_pattern: str             # 意图模式（如 "创建.*裂变.*任务"）
    trigger_keywords: List[str]     # 触发关键词

    # 执行计划
    plan: List[TaskSpec]            # 完整的步骤列表
    param_mappings: Dict[str, str]  # 参数映射规则（如 "人数" -> "target_count"）

    # 元数据
    success_count: int = 0          # 成功执行次数
    last_used: float = 0            # 最后使用时间
    created_at: float = 0           # 创建时间
    confidence: float = 1.0         # 置信度（多次成功后提升）
```

### 3.2 PathMatcher（路径匹配器）

```python
class PathMatcher:
    """匹配用户输入与已保存的执行路径"""

    def match(self, user_input: str, user_id: str, agent_id: str) -> Optional[ExecutionPath]:
        """
        匹配逻辑：
        1. 关键词匹配：检查 trigger_keywords
        2. 意图模式匹配：正则匹配 intent_pattern
        3. 语义相似度：使用 embedding 计算相似度
        4. 置信度阈值：只返回 confidence > 0.7 的路径
        """
        pass
```

## 4. 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户输入                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PathMatcher（新增）                           │
│  1. 检索已保存的 ExecutionPath                                   │
│  2. 匹配用户输入                                                 │
│  3. 返回最佳匹配路径（如有）                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
        [有匹配路径]                      [无匹配路径]
              │                               │
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────────────┐
│   直接执行已保存路径      │     │   正常流程：意图识别 → 规划      │
│   (跳过规划阶段)         │     │                                 │
└─────────────────────────┘     └─────────────────────────────────┘
              │                               │
              └───────────────┬───────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      任务执行                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PathRecorder（新增）                           │
│  任务成功完成后：                                                │
│  1. 提取执行路径（Plan + 参数映射）                              │
│  2. 生成意图模式和关键词                                         │
│  3. 保存到 ExecutionPathStore                                   │
│  4. 同步到 ProceduralMemory（可选）                             │
└─────────────────────────────────────────────────────────────────┘
```

## 5. 存储设计

### 5.1 ExecutionPathStore

```python
class ExecutionPathStore:
    """执行路径存储（基于 YAML + Embedding）"""

    def __init__(self):
        self.paths_dir = Path("execution_paths")  # 或使用数据库
        self.model = SentenceTransformer(...)     # 复用现有 embedding 模型
        self.paths: List[ExecutionPath] = []
        self.embeddings: np.ndarray = None

    def save_path(self, path: ExecutionPath) -> str:
        """保存执行路径"""
        # 1. 生成 embedding（基于 intent_pattern + trigger_keywords）
        # 2. 保存到 YAML 文件
        # 3. 更新内存索引
        pass

    def search(self, query: str, user_id: str, agent_id: str, limit: int = 3) -> List[ExecutionPath]:
        """搜索匹配的执行路径"""
        # 1. 计算 query embedding
        # 2. 余弦相似度匹配
        # 3. 过滤 user_id 和 agent_id
        # 4. 返回 top-k 结果
        pass

    def update_stats(self, path_id: str, success: bool):
        """更新路径统计（成功/失败次数）"""
        pass
```

### 5.2 YAML 存储格式

```yaml
# execution_paths/user_123_fission_task.yaml
path_id: "user_123_fission_task_001"
user_id: "user_123"
agent_id: "user_strat_fission"

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
    type: "MCP"
    executor: "create_fission_task"
    description: "创建裂变任务"

param_mappings:
  "人数": "target_count"
  "奖励": "reward_amount"
  "活动名": "task_name"

success_count: 5
last_used: 1706428800.0
confidence: 0.95
```

## 6. 与现有系统集成

### 6.1 集成点

| 组件 | 集成方式 |
|------|----------|
| **TaskRouter** | 在分发任务前调用 PathMatcher |
| **AgentActor** | 任务完成后调用 PathRecorder |
| **CommonTaskPlanner** | 规划时参考 ProceduralMemory |
| **ProceduralStore** | 复用现有的 embedding 和存储机制 |

### 6.2 TaskRouter 集成

```python
# task_router.py

def _handle_new_task(self, msg: RouterNewTaskMessage, sender: ActorAddress):
    # === 新增：路径匹配 ===
    path_matcher = get_path_matcher()
    matched_path = path_matcher.match(
        user_input=msg.user_input,
        user_id=msg.user_id,
        agent_id=msg.agent_id
    )

    if matched_path and matched_path.confidence > 0.8:
        # 直接使用已保存的路径执行
        self._execute_saved_path(matched_path, msg, sender)
        return

    # 正常流程...
```

### 6.3 AgentActor 集成

```python
# agent_actor.py

def _handle_task_completed(self, msg: TaskCompletedMessage):
    if msg.status == "SUCCESS":
        # === 新增：保存执行路径 ===
        path_recorder = get_path_recorder()
        path_recorder.record_success(
            user_id=self._user_id,
            agent_id=self._agent_id,
            original_input=self._original_input,
            plan=self._executed_plan,
            step_results=self._step_results
        )
```

## 7. 与 ProceduralMemory 的关系

### 7.1 区别

| 特性 | ExecutionPath | ProceduralMemory |
|------|---------------|------------------|
| **粒度** | 完整任务流程 | 单个操作步骤 |
| **用途** | 直接复用执行 | 辅助规划参考 |
| **匹配方式** | 精确匹配 + 语义 | 纯语义检索 |
| **存储内容** | Plan + 参数映射 | 步骤描述 |

### 7.2 协同工作

```
用户输入: "帮我创建一个裂变任务，拉5个人"
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: ExecutionPathStore.search()                             │
│         → 找到完全匹配的路径？                                   │
│         → YES: 直接执行                                         │
│         → NO: 继续 Step 2                                       │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: ProceduralMemory.search()                               │
│         → 找到相关的操作步骤？                                   │
│         → 作为规划参考，注入到 Planner prompt                    │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: CommonTaskPlanner.plan()                                │
│         → 生成新的 Plan                                         │
│         → 执行成功后保存到 ExecutionPathStore                    │
└─────────────────────────────────────────────────────────────────┘
```

## 8. 参数动态提取

执行已保存路径时，需要从用户输入中提取参数：

```python
class ParamExtractor:
    """从用户输入中提取参数"""

    def extract(self, user_input: str, param_mappings: Dict[str, str]) -> Dict[str, Any]:
        """
        使用 LLM 从用户输入中提取参数

        示例：
        user_input: "帮我创建一个裂变任务，拉5个人，奖励10元"
        param_mappings: {"人数": "target_count", "奖励": "reward_amount"}

        返回: {"target_count": 5, "reward_amount": 10}
        """
        prompt = f"""
        从以下用户输入中提取参数：

        用户输入：{user_input}

        需要提取的参数：
        {json.dumps(param_mappings, ensure_ascii=False)}

        请以 JSON 格式返回提取的参数值。
        """
        # 调用 LLM 提取
        pass
```

## 9. 置信度管理

```python
class ConfidenceManager:
    """管理执行路径的置信度"""

    def update_on_success(self, path: ExecutionPath):
        """成功执行后提升置信度"""
        path.success_count += 1
        path.confidence = min(1.0, path.confidence + 0.05)
        path.last_used = time.time()

    def update_on_failure(self, path: ExecutionPath):
        """失败后降低置信度"""
        path.confidence = max(0.0, path.confidence - 0.2)

        # 置信度过低时标记为不可用
        if path.confidence < 0.3:
            path.disabled = True

    def decay_unused(self, path: ExecutionPath, days_unused: int):
        """长期未使用的路径置信度衰减"""
        if days_unused > 30:
            path.confidence *= 0.9
```

## 10. 实现计划

### Phase 1: 基础存储（优先）
- [ ] 定义 ExecutionPath 数据结构
- [ ] 实现 ExecutionPathStore（YAML + Embedding）
- [ ] 实现基本的 save/search 接口

### Phase 2: 路径记录
- [ ] 实现 PathRecorder
- [ ] 在 AgentActor 任务完成后调用
- [ ] 自动生成 intent_pattern 和 trigger_keywords

### Phase 3: 路径匹配与执行
- [ ] 实现 PathMatcher
- [ ] 在 TaskRouter 中集成
- [ ] 实现 ParamExtractor

### Phase 4: 置信度与优化
- [ ] 实现 ConfidenceManager
- [ ] 添加失败回退机制
- [ ] 与 ProceduralMemory 协同

## 11. 文件结构

```
tasks/
├── capabilities/
│   └── execution_path/              # 新增模块
│       ├── __init__.py
│       ├── interface.py             # IExecutionPathCapability
│       ├── execution_path.py        # ExecutionPath 数据结构
│       ├── path_store.py            # ExecutionPathStore
│       ├── path_matcher.py          # PathMatcher
│       ├── path_recorder.py         # PathRecorder
│       ├── param_extractor.py       # ParamExtractor
│       └── confidence_manager.py    # ConfidenceManager
├── execution_paths/                 # 存储目录
│   └── *.yaml
```

## 12. 风险与缓解

| 风险 | 缓解措施 |
|------|----------|
| 路径过时（Agent 结构变化） | 定期验证路径有效性，失败时自动降低置信度 |
| 参数提取错误 | 提取后验证参数完整性，缺失时回退到正常流程 |
| 存储膨胀 | 限制每用户路径数量，清理低置信度路径 |
| 误匹配 | 设置高置信度阈值（0.8），支持用户确认 |

## 13. 总结

本方案通过引入 ExecutionPath 概念，实现：
1. **快速复用**：相似任务直接使用已验证的执行路径
2. **渐进学习**：成功执行提升置信度，失败降低
3. **与现有系统兼容**：复用 ProceduralStore 的 embedding 机制
4. **低侵入性**：主要在 TaskRouter 和 AgentActor 添加钩子
