# Changelog

---
## [2026-02-04 15:55] - Analytics 分析视图实现

### 任务描述
实现前端 Analytics 分析视图，展示系统级统计数据，包括系统总览、趋势图、Agent 排行榜、最近 Trace 列表。

### 修改文件
- [x] front/src/features/Analytics/index.vue - 新建 Analytics 视图组件
- [x] front/src/App.vue - 导入 Analytics 组件并添加视图切换

### 视图功能

**系统总览卡片（4列）**
- Agent 状态：总数、在线/离线数量、状态条
- 运行中：运行中 Trace 数、待处理任务数
- 今日任务：总任务数、成功/失败数
- 成功率：今日成功率、平均耗时

**7天趋势图**
- 柱状图展示每日任务数
- 成功/失败分色显示
- 日期和数量标签

**活跃 Agent 排行榜**
- Top 5 活跃 Agent
- 显示任务数、平均耗时、成功率
- 排名徽章（金银铜）

**最近 Trace 列表**
- 表格展示最近 5 个 Trace
- 显示状态、任务数、状态分布、深度、耗时、创建时间

### API 调用
```javascript
// 系统总览
GET /api/v1/stats/system/overview

// 7天趋势
GET /api/v1/stats/system/trend?days=7

// Top Agents
GET /api/v1/stats/system/top-agents?limit=5&days=7

// 最近 Traces
GET /api/v1/stats/traces/recent?limit=5
```

### 状态
✅ 完成 (2026-02-04 15:55)

---
## [2026-02-04 15:45] - Agent 监控面板指标增强

### 任务描述
为 Agent 监控面板设计并实现完整的 Agent 级监控指标，包括负载、性能、健康、实时状态四大类指标。

### 修改文件
- [x] events/services/agent_monitor_service.py - 新增 `get_agent_monitor_metrics()` 和 `get_batch_agent_metrics()` 方法
- [x] events/entry/api/v1/queries.py - 新增 `/agents/{agent_id}/metrics` 和 `/agents/batch-metrics` API 端点
- [x] front/src/utils/agentDataUtils.js - 新增 `extractAgentIds()`、`getLoadLevelColor()`，更新 `mapToNodeData()` 和 `processAgentTree()` 支持监控指标
- [x] front/src/api/agent.js - 新增 `getAgentMetrics()` 和 `getBatchAgentMetrics()` API 调用
- [x] front/src/features/TreeEditor/nodes/TreeNode.vue - 重构卡片布局，添加完整监控指标显示

### 指标设计

**负载指标 (load)**
| 指标 | 说明 |
|------|------|
| queue_depth | 待处理任务数 |
| load_level | 负载等级 (LOW/MEDIUM/HIGH) |
| next_tasks | 接下来的任务预览 |

**性能指标 (performance)**
| 指标 | 说明 |
|------|------|
| today_completed | 今日完成任务数 |
| today_success | 今日成功数 |
| today_failed | 今日失败数 |
| success_rate | 成功率 % |
| avg_duration_ms | 平均耗时 (毫秒) |

**健康指标 (health)**
| 指标 | 说明 |
|------|------|
| recent_failures | 最近1小时失败数 |
| consecutive_failures | 连续失败次数 |
| is_healthy | 是否健康 |

**实时指标 (realtime)**
| 指标 | 说明 |
|------|------|
| status | 状态 (IDLE/BUSY/OFFLINE) |
| is_online | 是否在线 |
| current_task | 当前任务信息 |
| task_progress | 任务进度 % |
| task_elapsed_ms | 已耗时 |
| task_eta_ms | 预估剩余时间 |
| is_overtime | 是否超时 |

### 卡片布局更新

```
┌─────────────────────────────────────┐
│ [类型]                    #agent_id │
│ Agent 名称                          │
│ Agent: xxx                          │
├─────────────────────────────────────┤
│ BUSY ● LIVE (5s ago) ⚠️ 2 fails    │
├─────────────────────────────────────┤
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│ │   12    │ │   95%   │ │  2.3s   │ │
│ │今日完成 │ │ 成功率  │ │平均耗时 │ │
│ └─────────┘ └─────────┘ └─────────┘ │
├─────────────────────────────────────┤
│ 队列: 3 个待处理        [████] HIGH │
├─────────────────────────────────────┤
│ 当前任务                            │
│ 数据清洗任务                        │
│ 65%  30s elapsed  ETA: 15s          │
│ [████████████░░░░░░░░]              │
├─────────────────────────────────────┤
│ ▼ 任务详情                          │
│ ▼ Meta Info                         │
└─────────────────────────────────────┘
```

### API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/traces/agents/{agent_id}/metrics` | GET | 获取单个 Agent 监控指标 |
| `/api/v1/traces/agents/batch-metrics` | POST | 批量获取多个 Agent 监控指标 |

### 状态
✅ 完成 (2026-02-04 15:45)

---
## [2026-02-04 15:45] - Agent 监控面板指标数据绑定

### 任务描述
修复 Agent 监控面板中每个卡片的指标数据（进度、耗时）始终显示为 0 的问题。

### 问题分析
- 后端 `AgentMonitorService` 已经在 `runtime_state.current_task` 中提供了丰富的指标数据
- 前端 `agentDataUtils.js` 的 `mapToNodeData` 函数将 `progress` 和 `timeElapsedMs` 硬编码为 `null` 和 `0`
- 需要正确提取后端数据并绑定到前端组件

### 修改文件
- [x] front/src/utils/agentDataUtils.js - 新增 `calculateElapsedMs()` 函数，修复 `visual` 对象的数据绑定
- [x] front/src/features/TreeEditor/nodes/TreeNode.vue - 更新 `Visual` 接口，添加时间格式化和 ETA 显示

### 关键修复

**1. agentDataUtils.js - 数据提取**
```javascript
// 新增 calculateElapsedMs 函数
function calculateElapsedMs(runtime_state) {
  // 优先使用 metrics.elapsed_seconds
  if (currentTask.metrics?.elapsed_seconds) {
    return currentTask.metrics.elapsed_seconds * 1000;
  }
  // 否则根据 start_time 计算
  if (currentTask.start_time) {
    return Math.max(0, Date.now() - currentTask.start_time * 1000);
  }
  return 0;
}

// visual 对象修复
visual: {
  progress: runtime_state.current_task?.progress ?? 0,
  timeElapsedMs: calculateElapsedMs(runtime_state),
  estimatedRemainingMs: (runtime_state.current_task?.metrics?.estimated_remaining_seconds ?? 0) * 1000,
  isOvertime: runtime_state.current_task?.metrics?.is_overtime ?? false,
  ...
}
```

**2. TreeNode.vue - 显示增强**
- 添加 `formatDuration()` 函数：将毫秒转换为人类可读格式（如 `2m 30s`）
- 添加 `elapsedDisplay` 和 `remainingDisplay` 计算属性
- 显示 ETA（预估剩余时间）和 OVERTIME（超时）标识

### 数据流
```
后端 AgentMonitorService
  → runtime_state.current_task.progress (进度)
  → runtime_state.current_task.metrics.elapsed_seconds (已耗时)
  → runtime_state.current_task.metrics.estimated_remaining_seconds (预估剩余)
  → runtime_state.current_task.metrics.is_overtime (是否超时)
    ↓
前端 agentDataUtils.mapToNodeData()
  → visual.progress
  → visual.timeElapsedMs
  → visual.estimatedRemainingMs
  → visual.isOvertime
    ↓
TreeNode.vue 组件显示
  → 进度百分比
  → 已耗时（格式化）
  → ETA（预估剩余时间）
  → OVERTIME 标识
```

### 状态
✅ 完成 (2026-02-04 15:45)

---
## [2026-02-04 15:30] - 总览界面指标 API 设计与实现

### 任务描述
设计并实现总览界面的统计指标 API，提供系统级、Agent级、Trace级的统计数据。

### 修改文件
- [x] events/entry/api/v1/stats.py - 新建统计 API 文件，包含完整的统计端点
- [x] events/main.py - 注册 stats_router 路由

### API 端点设计

**系统级统计**
| 端点 | 说明 |
|------|------|
| `GET /stats/system/overview` | 系统总览：Agent数量、运行中Trace、今日任务统计 |
| `GET /stats/system/daily?date=YYYY-MM-DD` | 指定日期的统计数据 |
| `GET /stats/system/trend?days=7` | 最近N天的趋势数据 |
| `GET /stats/system/top-agents?limit=10&days=7` | Top N 活跃 Agent |

**Agent级统计**
| 端点 | 说明 |
|------|------|
| `GET /stats/agents/{agent_id}/summary` | Agent 摘要：状态、今日统计 |
| `GET /stats/agents/{agent_id}/history?limit=20` | Agent 历史任务记录 |
| `GET /stats/agents/{agent_id}/metrics?days=7` | Agent 每日统计 |

**Trace级统计**
| 端点 | 说明 |
|------|------|
| `GET /stats/traces/{trace_id}/stats` | Trace 统计摘要 |
| `GET /stats/traces/recent?limit=10&status=RUNNING` | 最近的 Trace 列表 |

### 响应模型
- `SystemOverviewResponse`: 系统总览
- `DailyStatsResponse`: 每日统计
- `TrendDataResponse`: 趋势数据
- `AgentSummaryResponse`: Agent 摘要
- `AgentHistoryItem`: Agent 历史记录项
- `TraceSummaryStatsResponse`: Trace 统计摘要
- `TopAgentItem`: Top Agent 项
- `StatusDistribution`: 状态分布

### 状态
✅ 完成 (2026-02-04 15:30)

---
## [2026-02-04 12:22] - 多模块问题修复

### 任务描述
修复用户报告的8个问题：
1. interaction 的 health 端点返回 404
2. WebSocket 连接成功但不会自动变化
3. 前端 DAG 点击事件始终显示"无可用操作"
4. user_id 和 tenant_id 特殊处理 + React 循环上下文考虑
5. 总览界面指标设计
6. tokenizer 文件缺失错误 (No such file or directory)
7. Unknown database 'eqiai_agent' 错误
8. PlanCacheStore 无法实例化抽象类错误

### 修改文件
- [x] interaction/main.py - 在根路径添加 `/health` 端点（问题1）
- [x] tasks/capabilities/plan_cache/plan_cache_store.py - 实现 `initialize()` 和 `shutdown()` 抽象方法（问题8）
- [x] tasks/common/messages/task_messages.py - `ExecutionResultMessage.missing_params` 类型改为 `List[Any]` 支持字典格式（问题7的Pydantic验证错误）
- [x] tasks/capabilities/context_resolver/tree_context_resolver.py - 增强 `_build_context_summary_for_react()` 递归提取所有上下文值（问题4）
- [x] tasks/capabilities/execution/connect/base_connector.py - 将 `original_inputs` 合并到 `enriched_context` 确保已有参数被发现（问题4）
- [x] events/services/websocket_manager.py - 添加调试日志帮助诊断 WebSocket 推送问题（问题2）
- [x] tasks/capabilities/text_to_sql/vanna/local_embedding.py - 重写 `LocalONNXEmbeddingFunction`，不继承 `ONNXMiniLM_L6_V2`（问题6）

### 修改文件（续）
- [x] tasks/capabilities/context_resolver/tree_context_resolver.py - 新增 `_direct_match_params_from_context()` 直接匹配方法（问题4增强）
- [x] tasks/capabilities/execution/connect/base_connector.py - Step 4 修复：`None` 值视为解析失败，不更新到 filled_params（问题4增强）
- [x] tasks/capabilities/llm_memory/unified_manageer/manager.py - 记忆模块关键修复：
  - 修复未定义的函数调用 `create_vault_repo` → `build_vault_repo`
  - 修复资源记忆检索中的死代码 `return` 语句
  - 添加 Mem0 客户端初始化验证和降级机制
  - 增强所有记忆存储/检索方法的错误处理
  - 使用 logger 替代 print 语句

### 关键修复

**1. Health 端点 404**
```python
# interaction/main.py - 在主 app 上添加 /health（api_app 挂载在 /v1 下）
@app.get("/health", tags=["系统"])
async def health_check():
    return {"status": "healthy", "service": "interaction"}
```

**2. PlanCacheStore 抽象类错误**
```python
# plan_cache_store.py - 实现 CapabilityBase 的抽象方法
def initialize(self, config: Dict[str, Any]) -> None:
    if config.get("cache_dir"):
        self.cache_dir = Path(config["cache_dir"])
    self._load_all_caches()

def shutdown(self) -> None:
    self._model = None
    self._caches.clear()
    self._embeddings.clear()
```

**3. missing_params 类型错误**
```python
# task_messages.py - 支持 List[str] 或 List[Dict] 格式
missing_params: Optional[List[Any]] = None  # 原来是 List[str]
```

**4. React 循环上下文增强**
- `_build_context_summary_for_react()` 现在递归提取嵌套字典中的所有简单值
- `_resolve_all_params()` 将 `original_inputs` 合并到 `enriched_context`，确保已有参数值能被 ReAct 发现
- 新增 `_direct_match_params_from_context()` 方法：在 ReAct 之前先直接按参数名匹配
- Step 4 修复：`None` 值视为解析失败，不更新到 `filled_params`，避免覆盖已有值

**5. Tokenizer 文件缺失错误修复**
```python
# local_embedding.py - 完全重写，不继承 ONNXMiniLM_L6_V2
# 原因：父类 ONNXMiniLM_L6_V2 的 tokenizer 是 @cached_property，
# 会尝试从默认路径加载，导致 "No such file or directory" 错误

class LocalONNXEmbeddingFunction(EmbeddingFunction[Documents]):
    """完全自定义的本地 ONNX embedding function"""
    def __init__(self):
        self._model = None
        self._tokenizer = None

    def _ensure_model_loaded(self):
        # 延迟加载，从 EMBEDDING_MODEL_PATH 环境变量指定的路径加载
        ...
```

**6. 记忆模块关键修复**
```python
# manager.py - 修复未定义的函数调用
# 修复前：
self.vault_repo = vault_repo or create_vault_repo(config["vault"])  # NameError!

# 修复后：
from external.memory_store.memory_repos import build_vault_repo
self.vault_repo = vault_repo or build_vault_repo()

# 修复资源记忆检索中的死代码
# 修复前：
if "resource" in plan:
    return  # ← 这里无条件返回，后面的代码永远不执行！
    resource = self.get_resource_memory(...)

# 修复后：
if "resource" in plan:
    resource = self.get_resource_memory(user_id, plan["resource"])
    if resource:
        results["resource"] = resource

# 添加 Mem0 初始化验证
try:
    SHARED_MEM0_CLIENT = Memory.from_config(MEM0_CONFIG)
except Exception as e:
    logger.error(f"Failed to initialize Mem0 client: {e}")
    SHARED_MEM0_CLIENT = None  # 允许系统继续运行
```

**7. WebSocket 事件推送链路修复**
```python
# tasks/events/event_bus.py - 完善事件类型映射
event_type_mapping = {
    "TASK_CREATED": "CREATED",
    "TASK_PLANNING": "PLANNING",
    "TASK_DISPATCHED": "DISPATCHED",
    "TASK_RUNNING": "STARTED",
    "TASK_COMPLETED": "COMPLETED",
    "TASK_FAILED": "FAILED",
    "TASK_PROGRESS": "PROGRESS",
    "TASK_RESUMED": "RESUMED",
    "TASK_PAUSED": "PAUSED",
    "TASK_CANCELLED": "CANCELLED",
}

# events/services/observer_service.py - 添加更多事件类型处理
# 新增: CREATED, PLANNING, DISPATCHED, PAUSED, RESUMED, CANCELLED

# events/services/lifecycle_service.py - 添加更多事件类型的状态更新
# 新增: CREATED, PLANNING, DISPATCHED, PAUSED, RESUMED, CANCELLED

# events/common/enums.py - 添加 PAUSED 状态
class EventInstanceStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"  # 新增
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    SKIPPED = "SKIPPED"
```

### 待进一步排查
- ~~问题2（WebSocket 不自动变化）~~：✅ 已修复事件类型映射和处理
- ~~问题3（DAG 点击无可用操作）~~：✅ 已添加更多状态类型支持
- 问题5（总览界面指标设计）：需要单独设计
- ~~问题6（tokenizer 文件缺失）~~：✅ 已修复
- 问题7（Unknown database 'eqiai_agent'）：**数据配置问题**，需要：
  - 在 MySQL 中创建 `eqiai_agent` 数据库，或者
  - 修改 Neo4j 中 Agent 节点的 `database` 字段为正确的数据库名

### 状态
✅ 完成 (2026-02-04 14:30) - 核心代码修复完成

**已修复问题：**
1. ✅ interaction health 端点 404
2. 🔍 WebSocket 不自动变化（已添加日志，需运行时排查）
3. 🔍 DAG 点击无可用操作（需后端正确推送状态）
4. ✅ React 循环上下文增强 + None 值处理
5. ⏳ 总览界面指标设计（待单独设计）
6. ✅ tokenizer 文件缺失
7. 🔍 Unknown database 'eqiai_agent'（需检查 Neo4j 配置）
8. ✅ PlanCacheStore 抽象类错误
9. ✅ 记忆模块关键修复（函数调用、死代码、错误处理）

---
## [2026-02-03 17:09] - Neo4j 树节点新增 role 字段，AgentActor 规划时带上 role 和 memory

### 任务描述
1. 在 Neo4j 树节点解析中新增 `role` 字段
2. `AgentActor` 在调用 `TaskPlanner` 规划时，带上自己的 `role` 和 `memory`
3. `TaskPlanner` 在生成规划时，根据 Agent 的角色定位来制定更合适的计划

### 修改文件
- [x] tasks/agents/tree/node_service.py - `get_agent_meta` 新增 `role` 字段提取
- [x] tasks/agents/agent_actor.py - `_plan_task_execution` 获取并传递 `agent_role`
- [x] tasks/capabilities/task_planning/interface.py - `generate_execution_plan` 接口添加 `agent_role` 参数
- [x] tasks/capabilities/task_planning/common_task_planner.py:
  - `generate_execution_plan` 添加 `agent_role` 参数
  - `_semantic_decomposition` 添加 `agent_role` 参数
  - `_build_enhanced_planning_prompt` 添加角色定位部分到 prompt

### 关键设计

**Neo4j 节点新增字段**：
```python
meta = {
    "agent_id": node.get("agent_id"),
    "name": node.get("name", ""),
    "role": node.get("role", ""),  # 新增：Agent 角色定位
    ...
}
```

**规划 Prompt 增强**：
```
### 🎭 当前 Agent 角色定位
{agent_role}
*(请根据上述角色定位来制定规划。规划应符合该角色的职责范围和专业领域)*
```

**数据流**：
```
AgentActor._handle_task()
  → self.meta.get("role")  # 从 TreeManager 获取角色
  → _plan_task_execution(task_description, memory_context)
    → task_planner.generate_execution_plan(agent_id, user_input, memory_context, agent_role)
      → _semantic_decomposition(agent_id, user_input, memory_context, agent_role)
        → _build_enhanced_planning_prompt(user_input, memory, agents, agent_role)
```

### 状态
✅ 完成 (2026-02-03 17:20)

---
## [2026-02-03 16:31] - 增强 BaseConnector 参数填充：ReAct 式需求感知预填机制

### 任务描述
增强 `base_connector.py` 的参数填充逻辑，从"盲填"改为"ReAct 式需求感知"：
- 当前问题：参数填充只知道参数名和类型，不知道业务意图
- 期望效果：LLM 通过 ReAct 循环，结合业务需求和上下文，动态查找和推断参数值

例如：
- 用户说"查一下这个产品"，schema 要求 `product_id`
- ReAct 流程：分析需求 → 从上下文找到 product_name → 调用 QUERY 获取 ID → 填充参数

### 修改文件
- [x] tasks/capabilities/context_resolver/interface.py - `resolve_params_for_tool` 接口添加 `task_content` 和 `agent_id` 参数
- [x] tasks/capabilities/context_resolver/tree_context_resolver.py:
  - 重构 `resolve_params_for_tool`：增加 ReAct 式预填步骤
  - 重构 `_llm_infer_param_values`：改为 ReAct Agent，支持 INFER/EXTRACT/QUERY/FINISH 四种 Action
  - 新增 `_build_context_summary_for_react`：构建 ReAct 用的上下文摘要
  - 新增 `_build_react_prompt`：构建 ReAct Prompt
  - 新增 `_get_today_date`：获取当前日期用于时间类参数推断
- [x] tasks/capabilities/execution/connect/base_connector.py - 调用时传递 `task_content` 和 `agent_id` 参数

### 关键设计

**ReAct 流程**：
```
用户: "查一下这个产品的库存"
参数: product_id (必填)

ReAct 循环:
1. Thought: 用户提到"这个产品"，但没给 ID，需要从上下文找
2. Action: EXTRACT {"product_name": "enriched.product_name"}
3. Observation: product_name = "iPhone 15"
4. Thought: 有产品名但没 ID，需要调用查询
5. Action: QUERY {"product_id": "名称为 iPhone 15 的产品ID"}
6. Observation: product_id = "P12345"
7. Action: FINISH {"product_id": "P12345"}
```

**四种 Action**：
| Action | 用途 | 输入格式 |
|--------|------|----------|
| INFER | 直接推断值（时间、数量） | `{"param": "value"}` |
| EXTRACT | 从上下文路径提取 | `{"param": "global.xxx"}` |
| QUERY | 调用 resolve_context 查询 | `{"param": "查询描述"}` |
| FINISH | 完成填充 | `{"final_params": {...}}` |

**推断规则**：
- 时间类: "过去一个季度"→3个月前, "最近一周"→7天前
- 数量类: "所有"→1000或-1, "前N个"→N
- ID类: 优先 EXTRACT，其次 QUERY

### 状态
✅ 完成 (2026-02-03 16:50)

---
## [2026-02-03 15:43] - 步骤进度事件推送（使用 root_agent_id）

### 任务描述
在 `TaskGroupAggregatorActor` 中添加步骤进度事件推送，让前端能看到每一步的结果，同时不干扰现有的 `agent_id` 事件体系。

### 修改文件
- [x] tasks/capability_actors/task_group_aggregator_actor.py:
  - `_handle_step_success`: 添加 `TASK_PROGRESS` 事件推送，使用 `root_agent_id` 作为 `agent_id`
  - 新增 `_generate_result_summary` 方法生成结果摘要

### 关键设计
- 使用 `global_context["root_agent_id"]` 作为事件的 `agent_id`
- 这样事件会归属到父 Agent，不会创建新的节点
- 前端可以通过 `TASK_PROGRESS` 事件展示每一步的结果摘要

### 事件数据结构
```python
event_bus.publish_task_event(
    task_id=current_task.task_id,
    event_type=EventType.TASK_PROGRESS.value,
    agent_id=root_agent_id,  # 使用父 Agent 的 ID
    data={
        "step": step,
        "step_description": current_task.description,
        "step_result_summary": result_summary,
        "completed_steps": self.current_step_index + 1,
        "total_steps": len(self.sorted_subtasks),
        "executor": current_task.executor,
    }
)
```

### 状态
✅ 完成 (2026-02-03 15:43)

---
## [2026-02-03 15:37] - 撤销 TaskGroupAggregatorActor 事件推送

### 任务描述
撤销之前在 `TaskGroupAggregatorActor` 中添加的事件推送代码，因为会干扰现有的以 `agent_id` 为标识的事件上报体系。

### 修改文件
- [x] tasks/capability_actors/task_group_aggregator_actor.py:
  - 撤销 `_start_workflow` 中的事件推送
  - 撤销 `_handle_step_success` 中的事件推送
  - 撤销 `_finish_workflow` 中的事件推送
  - 撤销 `_fail_workflow` 中的事件推送
  - 删除 `_generate_result_summary` 方法
- [x] tasks/capabilities/execution/connect/dify_connector.py:
  - 删除 `_summarize_enriched_context` 方法
  - 删除 `_generate_value_summary` 方法
  - 传递完整 `enriched_context` 和 `step_results` 给 `_resolve_all_params`
  - 由 `TreeContextResolver.build_context_snapshot` 统一处理 Schema 摘要

### 关键说明
- 事件上报体系以 `agent_id` 为标识，由各个 `AgentActor` 和 `LeafActor` 负责上报
- `TaskGroupAggregatorActor` 只是内部的步骤聚合器，不应该直接推送事件
- Schema 摘要 + 按需展开机制已在 `TreeContextResolver` 中实现

### 状态
✅ 完成 (2026-02-03 15:37)

---
## [2026-02-03 15:22] - 修复补参数 JSON 格式暴露 + 启用事件推送 + Context 摘要优化

### 任务描述
修复三个核心问题：
1. 补参数请求返回 JSON 格式而非自然语言，且无法正确识别用户补参动作
2. 前端 DAG 无法自动更新（WebSocket 消息格式不匹配）
3. Context 膨胀问题（enriched_context 随任务执行不断增大）

### 修改文件

**问题1：补参数格式和识别**
- [x] tasks/capability_actors/execution_actor.py - `missing_params` 保持结构化字典格式 `[{"name": k, "description": v}]`
- [x] tasks/capability_actors/execution_actor1.py - 同上
- [x] interaction/services/task_result_handler.py - 增强 `_extract_need_input_info` 和 `_format_need_input_fallback`，支持解析字符串格式字典
- [x] interaction/capabilities/system_response_manager/common_system_response_manager.py - 改进 `generate_need_input_response`，过滤内部参数，显示参数描述
- [x] interaction/interaction_handler.py - 增强 `_resume_task_with_input`，添加辅助函数正确提取参数名
- [x] interaction/capabilities/intent_recognition_manager/common_intent_recognition_manager.py - 增强 `_format_context_for_llm`，正确提取参数名

**问题2：事件推送启用**
- [x] tasks/capability_actors/task_group_aggregator_actor.py:
  - 启用 `_start_workflow` 工作流启动事件
  - 启用 `_handle_step_success` 步骤成功事件（含结果摘要）
  - 启用 `_finish_workflow` 工作流完成事件
  - 启用 `_fail_workflow` 工作流失败事件
  - 新增 `_generate_result_summary()` 方法

**问题3：Context 摘要优化**
- [x] tasks/common/context/context_entry.py - 增强 `ContextEntry`：
  - 添加 `summary` 字段
  - 添加 `get_summary()` 方法
  - 添加 `to_summary_dict()` 方法
  - 新增 `create_context_entry_with_summary()` 工厂函数
- [x] tasks/capabilities/execution/connect/dify_connector.py:
  - 传递完整 `enriched_context` 和 `step_results` 给 `_resolve_all_params`
  - 由 `TreeContextResolver.build_context_snapshot` 统一处理 Schema 摘要
  - 新增 `_truncate_for_log()` 方法用于日志截断
- 注意：Schema 摘要 + 按需展开机制已在 `TreeContextResolver` 中实现，`dify_connector` 只需传递完整上下文

**问题4：前端 WebSocket 消息处理**
- [x] front/src/features/DagEditor/index.vue:
  - 修复 `handleWebSocketMessage` 兼容后端消息格式
  - 添加 `mapStatusToNodeStatus` 状态映射函数
  - 支持 `node_updated`、`graph_updated` 等新事件类型

**问题5：后端 ObserverService 事件处理**
- [x] events/services/observer_service.py:
  - 添加 `STARTED`、`RUNNING`、`COMPLETED`、`FAILED` 事件类型支持
  - 添加 `PROGRESS` 事件处理，携带步骤详情
  - 增强消息内容，包含 `name`、`message`、`step_result_summary` 等

### 关键修复

**1. 补参数格式修复**
```python
# 修复前：转成字符串，无法解析
missing_params_descriptions = [str({"name": k, "description": v}) for k, v in missing_params.items()]

# 修复后：保持结构化格式
missing_params_list = [{"name": k, "description": v} for k, v in missing_params.items()]
```

**2. 事件推送启用**
```python
# 步骤成功事件
event_bus.publish_task_event(
    task_id=current_task.task_id,
    event_type=EventType.TASK_PROGRESS.value,
    data={
        "step": step,
        "step_description": current_task.description,
        "step_result_summary": result_summary,  # 使用摘要
        "completed_steps": self.current_step_index + 1,
        "total_steps": len(self.sorted_subtasks)
    }
)
```

**3. Context 摘要机制**
```python
# 传递摘要版本给 LLM，减少 token 消耗
summarized_enriched_context = self._summarize_enriched_context(enriched_context)
full_context = {
    "enriched_context": summarized_enriched_context,  # 摘要版本
    "enriched_context_full": enriched_context,  # 完整版本用于按需展开
}
```

**4. 前端 WebSocket 消息兼容**
```javascript
// 兼容两种消息格式
const eventType = data.event || data.event_type || data.type;
const payload = data.data || data.payload || data;

switch (eventType) {
    case 'node_updated':  // 新格式
        updateNodeStatus(payload.node_id, mapStatusToNodeStatus(payload.status), payload.progress);
        break;
    case 'TASK_RUNNING':  // 旧格式兼容
        updateNodeStatus(payload.task_id, 'running', payload.progress || 50);
        break;
}
```

### 状态
✅ 完成 (2026-02-03 15:22)

---
## [2026-02-03 15:00] - 更新 API Key

### 任务描述
将项目中的旧 API Key 替换为新的 Key。

### 修改文件
- [x] .env.local - DASHSCOPE_API_KEY, MEM0_API_KEY
- [x] .env.prod - DASHSCOPE_API_KEY, MEM0_API_KEY
- [x] tasks/config.json - api_key

### 状态
✅ 完成 (2026-02-03 15:00)

---
## [2026-01-29 11:37] - 重构 NEED_INPUT 处理：遵循 Capability 架构

### 任务描述
重构之前的实现，遵循系统的 Capability 架构设计：
1. 消息格式化移到 `SystemResponseManager` capability
2. 状态拦截复用 `IntentRecognitionManager` 的意图判断逻辑
3. 支持用户在 NEED_INPUT 状态下选择：提供参数、取消任务、修改任务

### 修改文件
- [x] interaction/capabilities/system_response_manager/interface.py - 添加 generate_need_input_response() 接口
- [x] interaction/capabilities/system_response_manager/common_system_response_manager.py - 实现 generate_need_input_response()，添加 need_input prompt 模板
- [x] interaction/services/task_result_handler.py - 调用 capability 而非直接格式化
- [x] interaction/capabilities/intent_recognition_manager/common_intent_recognition_manager.py - 扩展 judge_special_intent 支持 NEED_INPUT 状态，添加 PROVIDE_INPUT 意图
- [x] interaction/interaction_handler.py - 统一状态拦截器，处理 awaiting_task_input 状态

### 关键修改

**1. SystemResponseManager 新增方法**
```python
def generate_need_input_response(
    self, session_id: str, trace_id: str,
    missing_params: List[str], completed_params: Dict = None
) -> SystemResponseDTO:
    # 格式化为自然语言，使用 LLM 美化
```

**2. IntentRecognitionManager 扩展**
- `_format_context_for_llm()`: 添加对 `awaiting_task_input` 状态的描述
- `judge_special_intent()`: 在 NEED_INPUT 状态下返回 `PROVIDE_INPUT`/`CANCEL`/`MODIFY`
- `_fallback_keyword_match()`: 降级关键字匹配逻辑

**3. 统一状态拦截器流程**
```
用户输入 → 检查 awaiting_task_input 状态
    ├─ PROVIDE_INPUT → 恢复任务执行
    ├─ CANCEL → 取消任务，清除状态
    ├─ MODIFY → 清除状态，提示重新描述
    └─ 其他 → 继续正常意图识别
```

**4. 用户可选操作**
- 直接输入参数值 → 系统识别为 PROVIDE_INPUT，恢复任务
- 说"取消"/"不要了" → 系统识别为 CANCEL，取消任务
- 说"修改"/"换一个" → 系统识别为 MODIFY，重新开始

### 状态
✅ 完成 (2026-01-29 11:44)

---
## [2026-01-29 11:00] - 修复 NEED_INPUT 消息格式和事件判断

### 任务描述
1. 回传给用户的 JSON 格式需要美化，使用自然语言展示而非直接展示 JSON
2. NEED_INPUT 事件未被正确识别，系统错误地创建了新任务而非暂停等待输入

### 问题分析
**问题1：消息格式**
- `task_result_handler.py` 中 NEED_INPUT 状态直接展示 JSON
- 需要使用 LLM 美化输出，或至少格式化为自然语言

**问题2：事件判断**
- `DialogStateDTO` 没有跟踪 NEED_INPUT 状态（只有 `waiting_for_confirmation`）
- 用户回复时走正常意图识别，而不是恢复任务
- 需要：
  1. 在 `DialogStateDTO` 添加 `awaiting_task_input` 字段跟踪 NEED_INPUT 状态
  2. 在 `task_result_handler.py` 收到 NEED_INPUT 时更新 dialog_state
  3. 在 `interaction_handler.py` 检测到 awaiting_task_input 时，恢复任务而非创建新任务

### 修改文件
- [x] interaction/common/response_state.py - DialogStateDTO 添加 awaiting_task_input 相关字段
- [x] interaction/services/task_result_handler.py - NEED_INPUT 时更新 dialog_state，美化消息格式
- [x] interaction/interaction_handler.py - 检测 awaiting_task_input 状态，调用恢复任务逻辑
- [x] interaction/external/client/task_client.py - resume_task 方法支持 parameters 参数
- [x] trigger/entry/api/routes.py - 添加 /traces/{trace_id}/resume-with-input 接口
- [x] trigger/services/lifecycle_service.py - 添加 resume_task_with_input 方法

### 关键修改

**1. DialogStateDTO 新增字段** (response_state.py)
```python
awaiting_task_input: bool = False
awaiting_task_trace_id: Optional[str] = None
awaiting_task_missing_params: Optional[List[str]] = None
awaiting_task_completed_params: Optional[Dict[str, Any]] = None
```

**2. NEED_INPUT 消息美化** (task_result_handler.py)
- `_format_need_input_message()`: 将 JSON 格式化为自然语言
- `_get_param_display_name()`: 参数名映射为中文显示名
- `_format_param_value()`: 格式化参数值

**3. 状态拦截器** (interaction_handler.py)
- 在意图识别前检测 `awaiting_task_input` 状态
- 如果为 True，调用 `_resume_task_with_input()` 恢复任务
- 恢复后清除状态并返回确认消息

**4. 任务恢复流程**
```
用户输入 → interaction_handler 检测 awaiting_task_input
    → TaskClient.resume_task(trace_id, parameters)
    → trigger /traces/{trace_id}/resume-with-input
    → lifecycle_service.resume_task_with_input()
    → RabbitMQ (work.excute, msg_type=RESUME_TASK)
    → tasks rabbitmq_listener._handle_resume_task()
    → TaskRouter.submit_resume_task()
```

### 状态
✅ 完成 (2026-01-29 11:30)

---
## [2026-01-28 22:45] - 修复 user_id 特殊格式未解析导致 Dify 报错

### 任务描述
修复 `user_id` 参数传递 `<user_id:1,tenant_id:1>` 格式字符串给 Dify，导致 Dify 后端报错 `For input string: "<user_id:1,tenant_id:1>"`

### 修改文件
- [x] tasks/capabilities/execution/connect/dify_connector.py - 添加 `_parse_special_format` 和 `_resolve_special_format_in_inputs` 方法

### 关键修复
1. 添加 `_parse_special_format()` 静态方法：解析 `<user_id:1,tenant_id:1>` 格式
2. 添加 `_resolve_special_format_in_inputs()` 方法：遍历所有 inputs，解析特殊格式
3. 在发送给 Dify 之前调用解析方法，确保 `user_id` 和 `tenant_id` 是实际值而非格式字符串

### 状态
✅ 完成 (2026-01-28 22:50)

---
## [2026-01-28 13:37] - 实现 AgentPlanCache 规划缓存

### 任务描述
实现 V2 方案：每个 AgentActor 独立管理自己的规划缓存

### 修改文件
- [x] tasks/capabilities/plan_cache/__init__.py - 模块初始化
- [x] tasks/capabilities/plan_cache/interface.py - IPlanCacheCapability 接口定义
- [x] tasks/capabilities/plan_cache/agent_plan_cache.py - AgentPlanCache 数据结构
- [x] tasks/capabilities/plan_cache/plan_cache_store.py - PlanCacheStore 存储实现
- [x] tasks/agents/agent_actor.py - 集成缓存查找和保存
- [x] tasks/execution_cache/agent_plans/.gitkeep - 缓存存储目录

### 关键实现

**AgentPlanCache 数据结构**
- `cache_id`: 唯一标识
- `agent_id`: 所属 Agent
- `task_description`: 原始任务描述
- `trigger_keywords`: 触发关键词
- `plan`: 规划结果（局部 Plan）
- `confidence`: 置信度（成功 +0.05，失败 -0.15）

**PlanCacheStore 存储**
- 按 agent_id 分目录存储 YAML 文件
- 支持语义相似度匹配（复用 all-MiniLM-L6-v2 模型）
- 支持关键词匹配作为回退

**AgentActor 集成**
- `_plan_task_execution()`: 优先查找缓存，未命中则规划并保存
- `_handle_task_result()`: 任务完成后更新缓存统计
- `_update_plan_cache_stats()`: 更新置信度

### 状态
✅ 完成 (2026-01-28 14:00)

---
## [2026-01-28 11:44] - 任务执行路径保存与记忆复用方案设计

### 任务描述
设计一个机制：
1. 保存已完成任务的执行路径，下次执行类似任务时直接复用
2. 利用记忆系统记住成功的处理模式

### 设计文档
- V1（已废弃）: `.claude/designs/task_path_memory_design.md`
- **V2（修正）**: `.claude/designs/task_path_memory_design_v2.md`

### V2 修正要点
**问题**：V1 忽略了系统的递归特性
- 系统是递归的：AgentActor → TaskGroupAggregator → ResultAggregator → AgentActor（子）
- 每个 AgentActor 独立规划，只知道自己的子节点
- 不能在 TaskRouter 层保存"完整执行路径"

**修正方案**：
- 保存粒度：每个 Agent 的**局部 Plan**，而非完整链路
- 集成点：**AgentActor._plan_task_execution()**，而非 TaskRouter
- 每层独立缓存，支持递归嵌套

### 核心概念
1. **AgentPlanCache**: 单个 Agent 的规划缓存（Plan + 意图模式 + 置信度）
2. **AgentPlanCacheStore**: 按 agent_id 分目录存储，支持语义匹配
3. 集成在 AgentActor 内部，不影响其他组件

### 执行流程
```
AgentActor._plan_task_execution()
    ├─ 查找 AgentPlanCache
    │   ├─ 命中 → 直接使用缓存的 Plan
    │   └─ 未命中 → TaskPlanner 规划 → 保存到缓存
    │
    └─ 任务完成后更新缓存统计（成功/失败）
```

### 状态
✅ 设计完成 V2 (2026-01-28 12:30) - 待用户确认后实现

---
## [2026-01-28 11:23] - 上下文参数解析优化：Schema 摘要 + 按需展开

### 任务描述
优化上下文传递和参数解析机制：
1. 传递完整上下文快照，不做预筛选
2. 使用 Schema 摘要让 LLM 快速了解数据结构，而不需要看完整内容
3. TreeContextResolver 提供统一的参数解析能力，供 MCPActor、CapabilityExecutor 等执行层使用
4. 按需从 step_results 提取实际值

### 修改文件
- [x] tasks/capabilities/context_resolver/interface.py - 添加新接口定义
- [x] tasks/capabilities/context_resolver/tree_context_resolver.py - 实现 Schema 摘要和参数解析
- [x] tasks/common/messages/task_messages.py - TaskMessage 添加 step_results 字段
- [x] tasks/capability_actors/mcp_actor.py - 使用新的参数解析接口
- [x] tasks/capability_actors/task_group_aggregator_actor.py - 传递 step_results
- [x] tasks/capability_actors/execution_actor.py - 添加 step_results 字段并传递给 connector
- [x] tasks/capabilities/execution/connect/base_connector.py - _resolve_all_params 使用新方案

### 关键设计
- `context_snapshot[step_id]._schema`: 数据结构摘要（类型信息）
- `context_snapshot[step_id]._ref`: 实际数据的引用路径
- `step_results`: 存储完整的步骤执行结果
- TreeContextResolver.resolve_params_for_tool(): 统一参数解析入口

### 新增方法
**TreeContextResolver:**
- `build_schema_summary(data)`: 从数据生成类型摘要
- `build_context_snapshot(step_results, global_context, enriched_context)`: 构建带 Schema 的上下文快照
- `resolve_params_for_tool(tool_schema, context_snapshot, step_results, task_description)`: 统一参数解析入口
- `get_missing_required_params(tool_schema, resolved_params)`: 获取缺失的必填参数

**MCPActor:**
- `_resolve_params_with_context_resolver(task_description)`: 使用新接口解析参数
- `_extract_and_resolve_params(task_description, context_snapshot, context_resolver)`: 提取并解析参数

### 状态
✅ 完成 (2026-01-28 12:00)

---
## [2026-01-28 10:30] - ContextEntry 存储优化

### 任务描述
优化 TaskGroupAggregatorActor 中的 ContextEntry 存储逻辑，避免上下文膨胀。

### 修改文件
- [x] tasks/capability_actors/task_group_aggregator_actor.py - 添加结果精简逻辑

### 关键修改

**task_group_aggregator_actor.py - 结果精简**
- `_simplify_result_for_context`: 递归精简结果，限制深度和长度
- `_extract_final_results_from_steps`: 从嵌套 step_results 提取最终有意义的结果
- 修改 `_enrich_context_from_result` 使用新的精简逻辑

优化策略：
1. 提取有意义的结果，避免存储完整的嵌套 step_results
2. 限制存储大小（字符串 1000 字符，列表 5 项，字典 10 字段）
3. 限制递归深度（默认 3 层）
4. 跳过冗余字段（step_results, enriched_context, global_context）

### 状态
✅ 完成 (2026-01-28 10:30)

---
## [2026-01-27 19:00] - 多项问题修复

### 任务描述
修复多个影响系统运行的问题：
1. ContextEntry 序列化问题
2. /health 接口缺失
3. 任务结果格式化
4. NEED_INPUT 状态处理

### 修改文件
- [x] tasks/capabilities/context_resolver/tree_context_resolver.py - 添加 `_safe_serialize_for_parsing` 方法
- [x] interaction/entry_layer/api_server.py - 添加 `/health` 和 `/v1/health` 接口
- [x] interaction/services/task_result_handler.py - 使用 SystemResponseManager 格式化任务结果
- [x] front/src/features/Copilot/index.vue - 支持 NEED_INPUT 状态处理

### 关键修改

**1. tree_context_resolver.py - 安全序列化**
```python
def _safe_serialize_for_parsing(self, obj: any) -> str:
    """处理 ContextEntry、Pydantic BaseModel 等不可直接 JSON 序列化的对象"""
    from pydantic import BaseModel
    def make_serializable(item):
        if isinstance(item, BaseModel):
            return item.model_dump()
        # ... 递归处理
    return json.dumps(make_serializable(obj), ensure_ascii=False)
```

**2. api_server.py - 健康检查接口**
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "interaction"}
```

**3. task_result_handler.py - 结果格式化**
- `_format_result_with_response_manager`: 使用 SystemResponseManager 格式化
- `_extract_meaningful_result`: 从嵌套 step_results 提取有意义内容
- `_summarize_step_results`: 汇总多步骤结果
- 支持 NEED_INPUT 状态

**4. Copilot/index.vue - NEED_INPUT 处理**
```javascript
if (data.status === 'NEED_INPUT') {
    resultMessage.status = 'need_input';
    const missingParams = data.need_input?.missing_params || [];
    resultMessage.content = `请补充以下信息：${missingParams.join('、')}`;
    aiStatus.value = 'waiting_input';
}
```

### 状态
✅ 完成 (2026-01-27 19:00)

---
## [2026-01-27 17:40] - 解析特殊格式的 user_id 占位符

### 任务描述
`pre_fill_known_params_with_llm` 无法正确解析 `<user_id:1,tenant_id:1>` 格式的占位符。

### 修改文件
- [x] tasks/capabilities/context_resolver/tree_context_resolver.py - 添加 `_parse_user_id_format` 方法

### 状态
✅ 完成 (2026-01-27 17:40)

---
## [2026-01-27 13:50] - 修复任务结果为字典时无法保存到对话历史的问题

### 任务描述
任务结果 `result` 可能是字典类型，而 `DialogTurn.utterance` 期望字符串，导致 Pydantic 验证错误。

### 修改文件
- [x] interaction/services/task_result_handler.py - `_save_result_to_history` 方法增加类型判断

### 关键修改

```python
# 构建结果消息（确保是字符串）
if status == "SUCCESS":
    if result is None:
        content = "任务执行完成"
    elif isinstance(result, str):
        content = result
    elif isinstance(result, dict):
        # 如果是字典，转为 JSON 字符串
        content = json.dumps(result, ensure_ascii=False, indent=2)
    else:
        content = str(result)
```

### 状态
✅ 完成 (2026-01-27 13:50)

---
## [2026-01-27 12:00] - 任务结果持久化到对话历史

### 任务描述
当 SSE 连接断开时，任务结果虽然被推送到队列，但用户刷新页面后无法看到结果。

### 解决方案
将任务结果保存到对话历史（持久化），这样即使 SSE 断开，用户刷新页面后也能从历史记录中看到任务结果。

### 修改文件
- [x] interaction/services/task_result_handler.py - 添加 `_save_result_to_history` 方法

### 关键修改

**task_result_handler.py**
- `_update_dialog_state`: 清除 `active_task_execution` 标记，调用 `_save_result_to_history`
- `_save_result_to_history`: 新方法，将任务结果作为系统消息保存到对话历史

```python
def _save_result_to_history(self, session_id, user_id, status, result, error):
    context_manager = capability_registry.get_capability("context_manager", IContextManagerCapability)

    content = result if status == "SUCCESS" else f"任务执行失败: {error}"

    system_turn = DialogTurn(
        session_id=session_id,
        user_id=user_id or "",
        role="system",
        utterance=content
    )
    context_manager.add_turn(system_turn)
```

### 状态
✅ 完成 (2026-01-27 12:00)

---
## [2026-01-27 11:15] - 修复 MCP Actor 中 ContextEntry 无法 JSON 序列化的问题

### 任务描述
MCP Actor 执行任务时报错：`TypeError: Object of type ContextEntry is not JSON serializable`

### 问题根源
`mcp_actor.py` 的 `_extract_params_with_llm` 方法中，直接使用 `json.dumps(context)` 序列化 context，但 context 可能包含 Pydantic `BaseModel` 对象（如 `ContextEntry`），这些对象无法直接被 JSON 序列化。

### 修改文件
- [x] tasks/capability_actors/mcp_actor.py - 添加 `_serialize_context` 方法处理复杂对象的序列化

### 关键修改

**mcp_actor.py - 添加递归序列化方法**
```python
def _serialize_context(self, context: Any) -> str:
    """将 context 转换为可 JSON 序列化的字符串"""
    from pydantic import BaseModel

    def make_serializable(obj: Any) -> Any:
        if obj is None:
            return None
        if isinstance(obj, (str, int, float, bool)):
            return obj
        if isinstance(obj, BaseModel):
            return obj.model_dump()  # Pydantic 模型转字典
        if isinstance(obj, dict):
            return {k: make_serializable(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [make_serializable(item) for item in obj]
        return str(obj)

    try:
        serializable = make_serializable(context)
        return json.dumps(serializable, ensure_ascii=False)
    except Exception as e:
        return str(context)
```

### 状态
✅ 完成 (2026-01-27 11:15)

---
## [2026-01-27 10:45] - 修复任务结果无法推送到前端的问题

### 任务描述
interaction 的 listener 接收到消息后，消息处理似乎没有起效，前端页面没有显示任务执行结果。

### 问题根源
1. **后端 SSE 推送逻辑缺陷**：`task_result_handler.py` 中检查 `if session_id in self.session_queues`，但 `SESSION_QUEUES` 是 `defaultdict(asyncio.Queue)`。当前端 SSE 连接不存在时，消息会被丢弃而不是缓存。
2. **前端未监听 task_result 事件**：前端只监听了 `thought` 和 `meta` 事件，但后端发送的任务结果事件类型是 `task_result`。

### 修改文件
- [x] interaction/services/task_result_handler.py - 移除 `if session_id in self.session_queues` 检查，始终将消息放入队列
- [x] front/src/features/Copilot/index.vue - 添加 `task_result` 事件监听和处理逻辑

### 关键修改

**1. task_result_handler.py - 修复 SSE 推送逻辑**
```python
# 之前：检查 session_id 是否在队列中，不存在则丢弃消息
if session_id in self.session_queues:
    ...
else:
    logger.debug(f"No active SSE connection for session: {session_id}")

# 之后：始终将消息放入队列（利用 defaultdict 特性自动创建队列）
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
```

**2. Copilot/index.vue - 添加 task_result 事件监听**
```javascript
events: ['thought', 'meta', 'task_result'],  // 添加 task_result

onEvent: (eventType, data) => {
  // 处理 task_result 事件（任务执行结果回传）
  if (eventType === 'task_result' && data) {
    console.log('Received task_result event:', data);
    const resultMessage = {
      id: Date.now(),
      role: 'ai',
      content: data.status === 'SUCCESS'
        ? (data.result || '任务执行完成')
        : `任务执行失败: ${data.error || '未知错误'}`,
      timestamp: new Date(),
      status: data.status === 'SUCCESS' ? 'completed' : 'error'
    };
    messages.value.push(resultMessage);
    scrollToBottom();
  }
},
```

### 状态
✅ 完成 (2026-01-27 10:45)

---
## [2026-01-26 16:00] - DagEditor 节点控制功能 + WebSocket 动态更新

### 任务描述
1. 在 DagEditor 的每个节点上添加右键菜单，允许用户控制节点（暂停/停止/继续）
2. 修复 DagEditor 不通过 WebSocket 动态更新的问题

### 修改文件
- [x] front/src/features/DagEditor/nodes/GlassNode.vue - 添加右键菜单、暂停状态图标和控制功能
- [x] front/src/api/order.js - 添加 controlSpecificNode API 函数
- [x] front/src/features/DagEditor/index.vue - 集成 WebSocket 动态更新节点状态

### 关键修改

**1. GlassNode.vue - 右键菜单控制**
- 添加 `paused` 状态支持
- 右键菜单显示：暂停（运行中）、继续（暂停时）、停止（运行中/暂停时）
- 直接调用 `controlSpecificNode` API
- 添加暂停状态覆盖层和脉冲动画

**2. order.js - 新增 API**
```javascript
export async function controlSpecificNode(traceId, instanceId, signal) {
  return request(`/traces/${traceId}/control/nodes/${instanceId}`, {
    method: 'POST',
    body: JSON.stringify({ signal }),
  }, EVENTS_API_BASE_URL);
}
```

**3. DagEditor/index.vue - WebSocket 集成**
- 建立 WebSocket 连接监听 trace 事件
- 处理事件类型：TASK_STARTED, TASK_COMPLETED, TASK_FAILED, TASK_PAUSED, TASK_CANCELLED, TASK_PROGRESS, TOPOLOGY_EXPANDED
- 实时更新节点状态和进度
- 组件卸载时自动清理 WebSocket 连接

### 状态
✅ 完成 (2026-01-26 16:30)

---
## [2026-01-26 15:30] - 修复 trace_session_mapping 表为空问题

### 任务描述
`trace_session_mapping` 表一直为空，导致 interaction 服务无法正确处理回传的消息。

### 问题根源
当用户确认任务执行时（`ack_immediately: True`），任务通过 `asyncio.create_task(_run_execute())` 异步执行，但 `_run_execute` 函数内部**没有保存 trace mapping**。

### 修改文件
- [x] interaction/interaction_handler.py - 在 `_run_execute` 异步函数中添加 trace mapping 保存逻辑（第 973-983 行）

### 关键修复
```python
# 在 _run_execute 异步函数中添加 trace mapping 保存
try:
    dialog_state_manager.dialog_repo.save_trace_mapping(
        request_id=request_id,
        session_id=input.session_id,
        user_id=input.user_id,
        trace_id=exec_context.external_job_id
    )
    logger.info(f"[ack_immediately] Saved trace mapping: ...")
except Exception as e:
    logger.warning(f"[ack_immediately] Failed to save trace mapping: {e}")
```

### 状态
✅ 完成 (2026-01-26 15:35)

---
## [2026-01-26 15:00] - 修复 Plan 生成不存在节点导致任务失败和上下文丢失

### 任务描述
Plan 中出现了不存在的节点 `mechanism_designer`，导致 LeafActor 初始化失败，进而导致上下文丢失。

### 问题根源
1. **Plan 生成无验证**：LLM 生成 plan 时，`executor` 字段由 LLM 直接生成，没有验证该节点是否真实存在
2. **LeafActor 空指针**：`self.meta` 为 `None` 时仍调用 `self.meta.get("name","")`，导致 `AttributeError`
3. **异常未捕获**：异常导致 `event_bus.publish_task_event()` 失败，任务状态未保存到 Redis
4. **上下文丢失**：后续任务无法从 Redis 加载状态

### 修改文件
- [x] tasks/capabilities/task_planning/common_task_planner.py - 在 plan 生成后验证 executor 存在性，添加模糊匹配和自动修复
- [x] tasks/agents/leaf_actor.py - 修复 NoneType 错误，`self.meta` 为 None 时使用 agent_id 作为备用名称

### 关键修复

**1. LeafActor 空指针修复** (leaf_actor.py:135-138)
```python
# 修复前：self.meta 为 None 时会抛出 AttributeError
name=self.meta.get("name",""),

# 修复后：使用 agent_id 作为备用名称
name=f"Unknown({self.agent_id})",
data={"error": f"Agent meta not found for '{self.agent_id}'", "status": "ERROR"}
```

**2. Plan 生成后验证 executor** (common_task_planner.py)
- 新增 `_validate_and_fix_executors()` 方法：验证 executor 是否存在于候选列表
- 新增 `_fuzzy_match_executor()` 方法：模糊匹配 executor 名称
- 如果 executor 不存在且无法匹配，跳过该步骤并记录错误日志

### 状态
✅ 完成 (2026-01-26 15:15)

---
## [2026-01-26 14:30] - 修复任务纠正不生效问题

### 任务描述
用户在创建裂变任务时，系统误解"5个人"为"团队5人"，用户多次纠正后系统仍然重复错误理解。

### 问题根源
1. `user_input_manager` 处理用户输入后生成 `enhanced_utterance`（LLM 理解后的增强版本）
2. `intent_recognition_manager` 的 `_build_result` 方法构建 `raw_nlu_output` 时，只包含 LLM 解析结果，**没有包含 `enhanced_utterance`**
3. `task_draft_manager` 的 `update_draft_from_intent` 尝试从 `intent_result.raw_nlu_output` 获取 `enhanced_utterance`，但该字段不存在
4. 导致系统使用 `original_utterance` 而非用户纠正后的理解

### 修改文件
- [x] interaction/interaction_handler.py - 在意图识别后，将 `session_state` 中的 `enhanced_utterance` 注入到 `intent_result.raw_nlu_output`（两处：`handle_user_input` 和 `stream_handle_user_input`）
- [x] interaction/capabilities/task_draft_manager/common_task_draft_manager1.py - 使用 `enhanced_utterance` 替代 `original_utterance` 进行草稿评估（之前已修复）

### 关键修复
```python
# interaction_handler.py - 在意图识别后注入 enhanced_utterance
intent_result.raw_nlu_output["enhanced_utterance"] = session_state.get("enhanced_utterance", input.utterance)
```

### 状态
✅ 完成 (2026-01-26 14:35)

---
## [2026-01-26 12:20] - 排查 agent_task_history 表为空问题

### 任务描述
排查为什么 `agent_task_history` 表一直为空，即使任务已经执行完成。

### 问题分析过程

1. **对比 git 版本**：对比 `38a4abaf` 与当前版本，发现只有 2 个提交：
   - 前端动画特效
   - events/config/settings.py 的 Pydantic v2 兼容性修复
   - 这些改动不会导致 agent 表为空

2. **追踪数据流**：
   - interaction → trigger (`/api/v1/ad-hoc-tasks`) → 创建 scheduled_task (PENDING)
   - schedule_scanner 扫描 PENDING 任务 → 发送到 `work.excute` 队列 → 更新为 SCHEDULED
   - tasks 服务监听 `work.excute` → 执行任务 → 发送事件到 events
   - events 的 `AgentMonitorService` 监听事件 → 写入 `agent_task_history`

3. **发现问题**：
   - 数据库中任务状态都是 `SCHEDULED`，不是 `PENDING`
   - `get_pending_tasks` 查询条件是 `status == "PENDING"` 且 `scheduled_time <= now`
   - 任务被扫描后立即更新为 `SCHEDULED`，说明扫描器正常工作
   - 但 tasks 服务没有收到消息

4. **根本原因**：
   - 任务确实被发送到 RabbitMQ，tasks 服务也收到并执行了
   - `AgentMonitorService` 只在 `TASK_COMPLETED` 或 `TASK_FAILED` 事件时才写入 `agent_task_history`
   - 之前测试的任务可能没有完成，或者事件没有正确传递 `agent_id`

5. **验证结果**：
   - 手动将一个任务状态改回 `PENDING` 触发重新执行
   - 任务执行完成后，`agent_task_history` 表成功写入数据
   - 表中现在有 6 条记录，包括 `private_domain`、`user_strat_fission` 等 agent

### 关键发现

- `AgentMonitorService.handle_event` 中的 "not handled" 日志只是提示性信息
- 只有 `TASK_COMPLETED` 和 `TASK_FAILED` 事件才会归档到 `agent_task_history`
- `TASK_STARTED`、`TASK_PROGRESS` 等事件会调用 `update_agent_state` 更新实时状态，但不写历史表

### 状态
✅ 完成 (2026-01-26 12:20) - 问题已解决，表中已有数据

---
## [2026-01-26 10:24] - 前端执行节点动态特效 + vanna 模型挂载修复

### 任务描述
1. 前端：为当前执行节点添加动态脉冲特效
2. vanna：修复 tokenizer 文件找不到的问题

### 修改文件
- [x] front/src/features/DagEditor/nodes/GlassNode.vue - 为 running 状态添加脉冲动画
- [x] docker-compose.yml - 添加 embedding 模型文件挂载

### 关键修复

**1. 前端动态特效**
```css
.status-running {
  animation: pulse-running 2s ease-in-out infinite;
}

@keyframes pulse-running {
  0%, 100% {
    box-shadow: 0 0 10px rgba(45, 212, 191, 0.2), 0 0 20px rgba(45, 212, 191, 0.1);
  }
  50% {
    box-shadow: 0 0 20px rgba(45, 212, 191, 0.4), 0 0 40px rgba(45, 212, 191, 0.2), 0 0 60px rgba(45, 212, 191, 0.1);
  }
}
```

**2. vanna 模型挂载**
```yaml
# docker-compose.yml tasks 服务
volumes:
  - ./all-MiniLM-L6-v2(1):/app/all-MiniLM-L6-v2(1):ro
```

### 待处理问题
- [ ] trace_session_mapping 表结构：需要手动删除旧表 `DROP TABLE trace_session_mapping;`，让服务重新创建
- [ ] agent 表数据为空：需要排查 Redis 连接、消息队列推送、AgentMonitorService 处理链路

### 状态
✅ 完成 (2026-01-26 10:24)

---
## [2026-01-23 17:56] - 修复 AgentMonitorService session 过早关闭导致无法写入数据库

### 任务描述
修复 events 服务的 agent_task_history 表没有数据的问题。

### 问题根源
在 `events/main.py` 中，创建 `AgentMonitorService` 时使用的 session 在 `finally` 块中被关闭，但 `task_history_repo` 和 `daily_metric_repo` 仍然持有这个已关闭的 session 引用，导致后续写入数据库失败。

### 修改文件
- [x] events/main.py
  - 移除 `finally` 块中的 `session.close()`
  - 在应用关闭时（yield 之后）关闭 session
  - 重命名变量为 `agent_monitor_session` 以区分

### 关键修复
```python
# 修复前：session 在 finally 中被关闭
try:
    task_history_repo = create_agent_task_history_repo(session, dialect)
    agent_monitor_svc = AgentMonitorService(...)
except Exception as e:
    ...
finally:
    await session.close()  # ❌ 这里关闭了 session，但 repo 还在使用

# 修复后：session 在应用关闭时才关闭
try:
    task_history_repo = create_agent_task_history_repo(agent_monitor_session, dialect)
    agent_monitor_svc = AgentMonitorService(...)
except Exception as e:
    await agent_monitor_session.close()
    raise
# 不在这里关闭 session

yield  # 应用运行中...

# 应用关闭时才关闭 session
await agent_monitor_session.close()
```

### 状态
✅ 完成 (2026-01-23 17:56)

---
## [2026-01-23 17:24] - 重构 trace_session_mapping 表结构，使用 request_id 作为主键

### 任务描述
修复 trace_id -> session_id 映射问题：
1. 数据库里没有值，映射没有保存
2. 设计问题：应该使用 request_id 作为主键，trace_id 作为关联字段

### 问题根源
原设计使用 `trace_id` 作为主键，但 `trace_id` 是任务提交后才获得的，而 `request_id` 是 interaction 服务自己生成的，更可控。

### 修改文件
- [x] interaction/external/database/dialog_state_repo.py
  - 修改表结构：`request_id` 作为主键，`trace_id` 作为可选字段
  - 修改 `save_trace_mapping`：接收 `request_id` 和可选的 `trace_id`
  - 新增 `update_trace_id`：更新映射中的 trace_id
  - 新增 `get_session_by_request`：根据 request_id 查询 session_id
  - 修改 `get_trace_mapping`：适应新的表结构
- [x] interaction/interaction_handler.py
  - 任务提交后同时保存 request_id 和 trace_id 到映射表

### 新表结构
```sql
CREATE TABLE trace_session_mapping (
    request_id VARCHAR(255) PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255),
    trace_id VARCHAR(255),
    created_at DOUBLE NOT NULL,
    INDEX idx_trace_session_mapping_session_id (session_id),
    INDEX idx_trace_session_mapping_trace_id (trace_id)
)
```

### 注意事项
- 需要手动删除旧表或执行迁移脚本
- 新部署后，旧的映射数据将丢失

### 状态
✅ 完成 (2026-01-23 17:24)

---
## [2026-01-23 17:14] - 修复 agent 表数据为空问题

### 任务描述
修复 events 服务的 agent_task_history 表没有数据的问题，导致无法正确推送任务历史。

### 问题根源
`ExecutionEventRequest` schema 中缺少 `name` 字段，导致 tasks 服务发送的任务名称无法被 events 服务接收和存储。

### 修改文件
- [x] events/entry/schemas/request.py - `ExecutionEventRequest` 添加 `name` 字段

### 关键修复
```python
# 添加 name 字段到 ExecutionEventRequest
name: Optional[str] = Field(None, description="任务/节点名称")
```

### 数据流说明
1. tasks 服务 `publish_task_event` 发送事件，包含 `agent_id` 和 `name`
2. events 服务 `lifecycle_service.sync_execution_state` 接收事件
3. `lifecycle_service` 发布事件到 `job_event_stream` topic
4. `agent_monitor_service` 监听事件，调用 `handle_task_completed_event`
5. `task_history_repo.create(payload)` 写入数据库

### 状态
✅ 完成 (2026-01-23 17:14)

---
## [2026-01-23 17:05] - 修复 trace_id -> session_id 映射查找失败问题

### 任务描述
修复 interaction 服务收到 RabbitMQ 任务结果消息后，无法找到对应的 session_id，导致无法推送到前端的问题。

### 问题根源
`interaction_handler.py` 中保存 trace 映射时，每次都创建新的 `DialogStateRepository()` 实例，而不是使用 `dialog_state_manager` 中已有的实例。虽然使用 MySQL 时理论上应该连接到同一个数据库，但这种做法不规范且可能导致连接池问题。

### 修改文件
- [x] interaction/interaction_handler.py - 使用 `dialog_state_manager.dialog_repo` 保存 trace 映射，而不是创建新实例
- [x] interaction/external/database/dialog_state_repo.py - 为 `save_trace_mapping` 和 `get_session_by_trace` 添加详细日志，便于调试

### 关键修复
```python
# 修复前：每次创建新实例
from external.database.dialog_state_repo import DialogStateRepository
dialog_repo = DialogStateRepository()
dialog_repo.save_trace_mapping(...)

# 修复后：使用 dialog_state_manager 的实例
dialog_state_manager.dialog_repo.save_trace_mapping(...)
```

### 状态
✅ 完成 (2026-01-23 17:05)

---
## [2026-01-23 16:14] - 修复 task_id 在链路传递中不一致导致有名节点状态不更新

### 任务描述
修复图节点显示问题：有名字的节点状态不更新（进度始终为 0%），而无名节点状态正常更新。

### 问题根源
`agent_actor.py` 中 `_build_task_group_request` 方法的调用顺序问题：
1. `_build_task_group_request` 为每个 plan 生成新的 `task_id`，但只存入 `task_clean` 字典
2. 原始的 `plan` 字典中**没有** task_id
3. 后续 `publish_task_event` 发送 `TASK_DISPATCHED` 事件时，`plans` 中没有 task_id
4. `event_bus._adapt_plan_to_meta` 使用 `plan.get("task_id", str(uuid.uuid4()))` 生成**另一个新的 UUID**
5. 导致 split 创建的节点（有名字）和后续事件使用的 task_id **不一致**

### 修改文件
- [x] tasks/agents/agent_actor.py - `_build_task_group_request` 中：
  - 在生成 task_id 后，写回原始的 `plan` 字典
  - 确保后续 `publish_task_event` 发送的 plans 中包含正确的 task_id

### 关键修复
```python
# 修复前：task_id 只存入 task_clean，plan 中没有
task_clean = {
    ...
    "task_id": str(uuid.uuid4()),  # 新生成的 UUID
}

# 修复后：先写入 plan，再使用
if "task_id" not in plan:
    plan["task_id"] = str(uuid.uuid4())  # 写回 plan
task_clean = {
    ...
    "task_id": plan["task_id"],  # 使用 plan 中的 task_id
}
```

### 状态
✅ 完成 (2026-01-23 16:14)

---
## [2026-01-23 15:09] - 修复图节点显示问题：无名节点和状态不更新

### 任务描述
修复任务执行图的两个显示问题：
1. 出现大量无名节点（name 字段为 NULL）
2. 带有名字的节点状态不更新（进度始终为 0%）

### 问题根源
1. **无名节点**：`sync_execution_state` 调用 `upsert_by_task_id` 时没有传递 `name` 字段，新创建的节点没有名称
2. **parent_id 引用错误**：`upsert_by_task_id` 创建新节点时使用 `root_node.id`（内部 UUID）而非 `root_node.task_id`（业务 ID），导致父子关系建立错误

### 修改文件
- [x] events/services/lifecycle_service.py - `sync_execution_state` 中提取 `name` 字段加入 `update_fields`
- [x] events/external/db/impl/postgres_impl.py - `upsert_by_task_id` 创建新节点时：
  - 添加 `name=fields.get("name")` 设置节点名称
  - 修正 `parent_id` 使用 `root_node.task_id` 而非 `root_node.id`
  - 修正 `node_path` 使用 `root_node.task_id` 而非 `root_node.id`

### 关键修复
```python
# lifecycle_service.py - 提取 name 字段
if "name" in execution_args and execution_args["name"]:
    update_fields["name"] = execution_args["name"]

# postgres_impl.py - 创建节点时设置 name 和正确的 parent_id
new_instance = EventInstanceDB(
    ...
    parent_id=root_node.task_id,  # 使用 task_id 而非 id
    node_path=f"{root_node.node_path}{root_node.task_id}/",
    name=fields.get("name"),  # 从 fields 中获取 name
    ...
)
```

### 状态
✅ 完成 (2026-01-23 15:09)

---
## [2026-01-23 14:40] - 统一 Redis 和 RabbitMQ 配置，修复 Events 服务使用 MockBus 问题

### 任务描述
修复多个配置问题：
1. Events 服务始终使用 MockBus 而非 RedisEventBus
2. Interaction 服务使用 Docker 内部 RabbitMQ，无法与 Tasks 服务通信
3. 各服务 Redis 配置不统一，部分使用硬编码值

### 问题根源
1. **MockBus 问题**：`events/event_config.json` 中 `use_redis: false`
2. **RabbitMQ 不通**：Interaction 使用 `rabbitmq:5672`（Docker 内部），Tasks 使用 `121.36.203.36:10005`（外部）
3. **Redis 配置混乱**：docker-compose.yml 中部分服务硬编码 Redis 地址

### 修改文件
- [x] events/event_config.json - `use_redis` 改为 `true`，更新 `redis_url` 和 `rabbitmq_url`
- [x] .env - 添加完整的 Redis 配置（REDIS_URL, REDIS_HOST, REDIS_PORT, REDIS_PASSWORD）
- [x] .env.local - 同步 Redis 和 RabbitMQ 配置
- [x] docker-compose.yml - 所有服务的 Redis 配置改为环境变量：
  - events 服务：REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_URL
  - interaction 服务：REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
  - tasks 服务：REDIS_HOST, REDIS_PORT, REDIS_DATABASE, REDIS_PASSWORD
  - trigger 服务：REDIS_HOST, REDIS_PORT, REDIS_URL

### 配置统一后
```
Redis: redis://:lanba888@121.36.203.36:10002/0
RabbitMQ: amqp://admin:Lanba%40123@121.36.203.36:10005/prod
```

### 状态
✅ 完成 (2026-01-23 14:40)

---
## [2026-01-23 14:20] - 修复任务进度显示和状态卡住问题

### 任务描述
修复两个问题：
1. 任务状态为 RUNNING 时，进度显示 0% 而不是 50%
2. 任务一直卡在 RUNNING 状态，没有变成 SUCCESS/FAILED

### 问题根源
1. **进度问题**：`TASK_RUNNING` 事件发布时没有设置 `progress` 字段，`lifecycle_service` 处理 `STARTED` 事件时也没有设置 `progress`
2. **状态卡住问题**：API 端点没有调用 `session.commit()`，导致数据库更新没有持久化

### 修改文件
- [x] tasks/agents/leaf_actor.py - TASK_RUNNING 事件添加 `progress: 50`
- [x] tasks/agents/agent_actor.py - TASK_RUNNING 事件添加 `progress: 50`
- [x] events/services/lifecycle_service.py - STARTED 事件处理时设置 `progress` (从 data 提取或默认 50%)
- [x] events/entry/api/v1/commands.py - 所有写操作端点添加 `session.commit()` 和 `session.rollback()`

### 关键修复
1. 进度更新：RUNNING 状态默认 50%，COMPLETED 状态 100%
2. 事务提交：所有写操作端点（start_trace, report_execution_event, control_whole_trace, split_task, control_specific_node）都添加了显式的 commit/rollback

### 状态
✅ 完成 (2026-01-23 14:20)

---
## [2026-01-23 13:50] - 修复任务状态一直为 PENDING 的问题

### 任务描述
修复数据库中任务状态一直显示为 PENDING，没有正确转换为 RUNNING/SUCCESS/FAILED 的问题。

### 问题根源
- `AgentActor` 和 `LeafActor` 只发布了 `TASK_CREATED` 事件，没有发布 `TASK_RUNNING` 事件
- 只有 `TASK_RUNNING` 事件才会被转换为 `STARTED`，进而更新状态为 `RUNNING`
- 状态转换链断裂：`PENDING` → (缺失 RUNNING) → 直接跳到 `SUCCESS/FAILED`

### 修改文件
- [x] tasks/agents/agent_actor.py - 在任务分发后添加 `TASK_RUNNING` 事件发布
- [x] tasks/agents/leaf_actor.py - 在发送给 ExecutionActor 前添加 `TASK_RUNNING` 事件发布

### 状态转换流程（修复后）
```
PENDING (初始状态)
    ↓ TASK_CREATED
PENDING
    ↓ TASK_RUNNING → 转换为 STARTED
RUNNING ← 状态正确更新
    ↓ TASK_COMPLETED → 转换为 COMPLETED
SUCCESS
```

### 状态
✅ 完成 (2026-01-23 13:50)

---
## [2026-01-23 11:53] - 修复三个核心问题：WebSocket推送、数据库切换、RabbitMQ连接

### 任务描述
修复三个影响系统正常运行的问题：
1. Events 服务的 WebSocket 消息推送问题
2. 数据库地址线上/本地切换支持
3. RabbitMQ 连接被重置（Connection reset by peer）

### 修改文件

**问题1: WebSocket 推送**
- [x] front/src/api/agent.js - 修复 WebSocket URL 构建，使用完整的 `ws://host/api/events/...`
- [x] front/src/utils/socket.js - 修复 trace WebSocket URL 路径
- [x] front/src/composables/useApi.js - 添加缺失的 `onMounted` 导入
- [x] front/src/features/Copilot/index.vue - 集成 WebSocket 监听任务状态更新
- [x] interaction/interaction_handler.py - 在 `meta` 事件中添加 `trace_id` 字段

**问题2: 数据库地址切换**
- [x] docker-compose.yml - 将硬编码的数据库配置改为从环境变量读取
- [x] .env - 更新为本地开发配置（公网 IP）
- [x] .env.local - 新建，本地开发配置
- [x] .env.prod - 新建，线上生产配置（内网 IP）
- [x] .env.docker - 删除（已被 .env.local/.env.prod 替代）

**问题3: RabbitMQ 连接**
- [x] tasks/external/message_queue/task_result_publisher.py - 添加心跳参数，改进重连机制
- [x] interaction/external/message_queue/task_result_listener.py - 增强错误处理和重连逻辑

### 关键决策
1. WebSocket URL 需要完整路径 `/api/events/api/v1/traces/ws/{traceId}`
2. 环境配置分离：`.env.local`（本地开发，公网IP）和 `.env.prod`（线上生产，内网IP）
3. RabbitMQ 连接统一使用 `heartbeat=600` 秒，防止心跳超时

### 使用方法
```bash
# 本地开发
cp .env.local .env && docker-compose up -d

# 线上部署
cp .env.prod .env && docker-compose up -d
```

### 状态
✅ 完成 (2026-01-23 11:53)

---
## [2026-01-22 14:24] - 统一各服务配置读取方式

### 任务描述
检查并修复各服务的配置读取方式，确保本地开发和 Docker 环境使用一致的 RabbitMQ 地址。

### 修改文件
- [x] interaction/main.py - 优先从环境变量 `RABBITMQ_URL` 读取，否则从配置文件读取
- [x] interaction/interaction_config.json - 默认 RabbitMQ 地址改为外部地址

### 检查结果
| 服务 | 状态 | 说明 |
|------|------|------|
| events | ✅ | 正确使用 `os.getenv("RABBITMQ_URL")` |
| trigger | ✅ | 正确使用 `os.getenv("RABBITMQ_URL")` |
| tasks | ✅ | 已修复，使用 `os.getenv("RABBITMQ_URL")` |
| interaction | ✅ | 已修复，优先使用环境变量 |

### 状态
✅ 完成 (2026-01-22 14:24)

---
## [2026-01-22 14:12] - 修复 tasks 服务 RabbitMQ 配置问题

### 任务描述
修复 tasks 服务无法从 RabbitMQ 接收消息的问题。所有服务统一使用外部 RabbitMQ。

### 修改文件
- [x] tasks/config.py - `RABBITMQ_URL` 改为从环境变量读取
- [x] docker-compose.yml - 所有服务的 `RABBITMQ_URL` 改为外部地址 `amqp://admin:Lanba%40123@121.36.203.36:10005/prod`

### 关键决策
1. 统一使用外部 RabbitMQ `121.36.203.36:10005/prod`
2. 移除对 Docker 内部 rabbitmq 服务的依赖

### 状态
✅ 完成 (2026-01-22 14:19)

---
## [2026-01-22 13:50] - 修复 tasks 服务无法连接 events 服务

### 任务描述
修复 tasks 服务的 event_bus 无法连接 events 服务的问题，错误信息：`All connection attempts failed`

### 修改文件
- [x] tasks/events/event_bus.py - 从环境变量 `EVENTS_SERVICE_URL` 读取 events 服务地址，而非使用硬编码的 `http://localhost:8004`

### 关键决策
1. 添加环境变量 `EVENTS_SERVICE_URL`，默认值为 `http://localhost:8000`
2. 在 Docker 环境中需要设置 `EVENTS_SERVICE_URL=http://events:8000`

### 状态
✅ 完成 (2026-01-22 13:50)

---
## [2026-01-22 11:55] - 修复 trigger 调用 events 服务报错

### 任务描述
修复 trigger 服务调用 events 服务的 `/api/v1/traces/start` 接口时报错的问题：
1. `user_id` 验证失败 - `Input should be a valid string`
2. `PostgreSQLEventInstanceRepository() takes no arguments`

### 修改文件
- [x] trigger/services/lifecycle_service.py - 添加从 `input_params._user_id` 提取 `user_id` 的 fallback 逻辑
- [x] events/external/db/impl/postgres_impl.py - 删除重复定义的 `PostgreSQLEventInstanceRepository` 类和孤立的残留代码

### 关键决策
1. 在 trigger 端添加 fallback 逻辑而非修改所有调用方，因为 `_user_id` 已经统一放在 `input_params` 中
2. 删除重复的类定义，保留第一个完整的实现

### 状态
✅ 完成 (2026-01-22 11:55)
