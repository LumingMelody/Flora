# Changelog

---
## [2026-01-20 17:52] - 视频混剪生成 Dify Workflow

### 任务描述
创建视频混剪生成 Workflow，用户只需输入主题/关键词，系统自动：
1. LLM 生成 tags 和文案
2. 从素材库匹配视频素材
3. 调用视频生成接口

### 修改文件

### 关键决策
1. 素材匹配策略：tag 搜索 → 名称搜索 → 通用素材兜底
2. LLM 生成所有文案和配置参数
3. 通用素材使用固定 tag "通用" 搜索

### 状态
✅ 完成 (2026-01-20)

---
## [2026-01-20 17:23] - 客户评价规则与打标 Dify Workflow

### 任务描述
创建两个 Dify Workflow 实现客户评价标准管理和自动打标功能：
1. 创建评价规则 Workflow - 根据行业生成客户评价标准并存库
2. 客户打标 Workflow - 根据规则给客户打标签

### 修改文件
- [x] dify_workflow/10.0.0客户评价规则创建.yml - 新建规则创建 Workflow
- [x] dify_workflow/10.0.1客户批量打标.yml - 新建客户打标 Workflow
- [x] dify_workflow/客户评价规则API设计.md - 新建 API 设计文档

### 关键决策
1. 两个独立 Workflow，规则可复用
2. 规则存储到外部数据库（设计了 CRUD API）
3. 打标支持单个和批量客户（自动判断使用哪个 API）
4. 使用 mark-tags / mark-tags-batch API

### 状态
✅ 完成 (2026-01-20)

---
## [2026-01-20 已完成] - 草稿描述动态更新机制

### 任务描述
为 TaskDraft 增加动态 description 更新机制，解决描述质量差、语义不连贯、无法预览、与槽位脱节等问题。

### 问题分析
原有 description 是在 `prepare_for_execution` 阶段通过简单拼接 `original_utterances` 生成的：
- 直接拼接用户多轮对话，包含无关内容（"好的"、"嗯"）
- 用户修正了之前的说法，但拼接不会反映修正
- description 只在最后执行时生成，用户无法提前确认
- 槽位变化后 description 没有同步更新

### 解决方案
1. 在 `TaskDraftDTO` 中新增 `description: Optional[str]` 字段
2. 新增 `_generate_description()` 方法，使用 LLM 生成高质量描述
3. 新增 `_fallback_description()` 方法，LLM 失败时降级到拼接逻辑
4. 在 `update_draft_from_intent` 末尾触发更新（单次只调用一次 LLM）
5. 在 `set_draft_pending_confirm` 状态变化时触发更新
6. 修改 `prepare_for_execution` 优先使用已生成的 description

### 修改文件
- [x] interaction/common/task_draft.py - 新增 `description: Optional[str] = None` 字段
- [x] interaction/capabilities/task_draft_manager/common_task_draft_manager.py
  - 新增 `_fallback_description()` 方法
  - 新增 `_generate_description()` 方法
  - 修改 `update_draft_from_intent()` 触发 description 更新
  - 修改 `set_draft_pending_confirm()` 触发 description 更新
  - 修改 `prepare_for_execution()` 优先使用已有 description

### 关键决策
1. **触发时机**：槽位变化时 + 状态变化时
2. **展示方式**：静默更新，仅在最终确认时展示
3. **生成方式**：LLM 生成
4. **调用优化**：单次 `update_draft_from_intent` 只触发一次 LLM 调用
5. **失败处理**：回退到拼接逻辑

### 状态
✅ 完成 (2026-01-20)

---
## [2026-01-20 已完成] - 修复 TaskRouterActor Resume 路由问题

### 任务描述
修复 `TaskRouterActor` 在处理 `NEED_INPUT` 后 resume 时，消息发送到错误 Actor 的问题。

### 问题分析
当 `LeafActor` 通过 `root_reply_to` 直接向 `TaskRouterActor` 发送 `NEED_INPUT` 时：
- `TaskRouterActor` 只保存了状态到 Redis
- **没有保存发送 NEED_INPUT 的 Actor 地址**
- Resume 时总是发送到 `AgentActor`，而不是原来暂停的 `LeafActor`

```
之前（错误）：
  LeafActor ──NEED_INPUT──► TaskRouter (不保存 sender)
  Resume ──► TaskRouter ──► AgentActor (错误！应该发到 LeafActor)

之后（正确）：
  LeafActor ──NEED_INPUT──► TaskRouter (保存 sender=LeafActor)
  Resume ──► TaskRouter ──► LeafActor (正确！)
```

### 解决方案
1. 新增 `_need_input_senders: Dict[str, ActorAddress]` 映射
2. 在 `_handle_task_completed` 中，当 `status == "NEED_INPUT"` 时保存 `sender`
3. 在 `_handle_resume_task` 中，优先从 `_need_input_senders` 获取目标 Actor
4. 在任务完成（SUCCESS/FAILED）时清理映射

### 修改文件
- [x] tasks/router/task_router.py
  - 新增 `_need_input_senders` 映射
  - 修改 `_handle_task_completed` 保存 sender
  - 修改 `_handle_resume_task` 优先使用保存的 sender
  - 在终态时清理映射

### 状态
✅ 完成 (2026-01-20)

---
## [2026-01-20 已完成] - 调度时间表达式解析增强

### 任务描述
增强 `CommonSchedule` 调度管理器的时间表达式解析能力，支持中文数字和相对日期表达式。

### 问题分析
原有的 `_extract_delay_seconds` 方法只能解析阿拉伯数字格式（如 "3天后"），无法解析：
- 中文数字：如 "三天后"、"五小时后"
- 相对日期：如 "这周五"、"下周一"、"明天"、"后天"

导致用户说 "三天后执行" 时，时间解析失败，任务被错误地调度到其他日期。

### 解决方案
1. 新增 `_chinese_to_number()` 方法，支持中文数字转阿拉伯数字
2. 新增 `_calculate_seconds_until_date()` 方法，计算到目标日期的秒数
3. 增强 `_extract_delay_seconds()` 方法，支持多种时间表达式
4. 更新 `_looks_like_schedule()` 正则，识别新的时间表达式
5. 更新 `_extract_interval_seconds()` 方法，支持中文数字

### 支持的时间表达式
| 表达式 | 示例 |
|--------|------|
| X天/小时/分钟/秒后 | "三天后"、"5小时后"、"十五分钟后" |
| 明天/后天/大后天 | "明天执行"、"后天开始" |
| 这周X/本周X/周X | "这周五"、"本周三"、"周日" |
| 下周X | "下周一"、"下周五" |

### 修改文件
- [x] interaction/capabilities/schedule_manager/common_schedule_manager.py
  - 新增 `_chinese_to_number()` 方法
  - 新增 `_calculate_seconds_until_date()` 方法
  - 增强 `_extract_delay_seconds()` 方法
  - 更新 `_extract_interval_seconds()` 方法
  - 更新 `_looks_like_schedule()` 正则表达式
  - 添加顶部 `datetime`, `timedelta` 导入

### 状态
✅ 完成 (2026-01-20)

---
## [2026-01-20 已完成] - RabbitMQ 配置统一与自动重连

### 任务描述
1. 统一各服务的 RabbitMQ 连接配置，使用 `env.py` 中的 `RABBITMQ_URL`
2. 为 `TaskResultListener` 添加自动重连机制

### 修改文件
- [x] env.py - 新增 `RABBITMQ_URL` 导出
- [x] interaction/main.py - 从 `env` 导入 `RABBITMQ_URL`
- [x] tasks/external/message_queue/task_result_publisher.py - 优先使用 `env.RABBITMQ_URL`
- [x] tasks/external/message_queue/rabbitmq_listener.py - 优先使用 `env.RABBITMQ_URL`
- [x] interaction/external/message_queue/task_result_listener.py - 添加自动重连机制

### 状态
✅ 完成 (2026-01-20)

---
## [2026-01-20 已完成] - NEED_INPUT 直接回报 TaskRouter 机制

### 任务描述
修复 `NEED_INPUT` 状态无法正确从 LeafActor 传导回 TaskRouter 的问题。

### 问题分析
原有方案使用 `trace_id_to_sender` 映射，但问题在于消息传递机制本身：
- `reply_to` 字段在每一层都被覆盖为 `self.myAddress`
- 导致 NEED_INPUT 需要逐层回传，中间层可能丢失或处理不当

执行链路：
```
TaskRouter (设置 reply_to=self)
  → AgentActor (覆盖 reply_to=self)
    → TaskGroupAggregator (覆盖 reply_to=self)
      → ResultAggregator (覆盖 reply_to=self)
        → LeafActor (返回 NEED_INPUT，但 reply_to 指向 ResultAggregator)
```

### 解决方案
新增 `root_reply_to` 字段，整个链路保持不变，指向 TaskRouter：
1. TaskMessage 新增 `root_reply_to` 字段
2. TaskRouter 设置 `root_reply_to = self.myAddress`
3. 各层 Actor 传递 `root_reply_to` 但不覆盖
4. LeafActor 在 NEED_INPUT 时使用 `root_reply_to` 直接发送给 TaskRouter

### 修改文件
- [x] tasks/common/messages/task_messages.py - 新增 `root_reply_to` 字段
- [x] tasks/router/task_router.py - 设置 `root_reply_to = self.myAddress`
- [x] tasks/agents/agent_actor.py - 传递 `root_reply_to`
- [x] tasks/capability_actors/task_group_aggregator_actor.py - 保存并传递 `root_reply_to`
- [x] tasks/capability_actors/result_aggregator_actor.py - 保存并传递 `root_reply_to`
- [x] tasks/agents/leaf_actor.py - 使用 `root_reply_to` 直接回报 NEED_INPUT

### 状态
✅ 完成 (2026-01-20)

---
## [2026-01-20 已完成] - 修复 AgentActor NEED_INPUT 传导问题

### 任务描述
修复 `NEED_INPUT` 状态无法正确从 LeafActor 传导回 TaskRouter 的问题。

### 问题分析
执行链路中 `task_id` 会发生变化：
```
TaskRouter (task_id=uuid-1)
  → AgentActor (保存 task_id_to_sender[uuid-1])
    → TaskGroupAggregator (生成新 task_id=step_1)
      → ResultAggregator
        → LeafActor (返回 task_id=step_1)
```

当 `NEED_INPUT` 返回时，`AgentActor` 使用 `task_id_to_sender.get("step_1")` 查找 sender，但映射中只有 `"uuid-1"`，导致找不到正确的 sender。

### 解决方案
使用 `trace_id`（整个链路不变）代替 `task_id` 来查找 sender：
1. 新增 `trace_id_to_sender` 映射
2. 在 `_handle_task` 中同时保存 `trace_id → sender` 映射
3. 在 `_handle_task_paused_from_execution` 和 `_handle_task_result` 中优先使用 `trace_id` 查找

### 修改文件
- [x] tasks/agents/agent_actor.py - 新增 `trace_id_to_sender` 映射，修改查找逻辑

### 状态
✅ 完成 (2026-01-20)

---
## [2026-01-19 已完成] - RabbitMQListener 适配 TaskRouterClient

### 任务描述
修复 RabbitMQListener 中调用 TaskRouter 的方法名，适配 Actor 模式重构后的 TaskRouterClient 接口。

### 修改文件
- [x] tasks/external/message_queue/rabbitmq_listener.py - 修复方法调用

### 修改内容
| 原方法 | 新方法 |
|--------|--------|
| `handle_new_task_async()` | `submit_new_task()` |
| `handle_resume_task_async()` | `submit_resume_task()` |

### 背景
TaskRouter 已重构为 Actor 模式（TaskRouterActor + TaskRouterClient），但 RabbitMQListener 中仍使用旧的方法名，导致运行时报错。

### 状态
✅ 完成 (2026-01-19)

---
## [2026-01-19 已完成] - Bug 修复：JSON 序列化和 Windows 文件名

### 任务描述
修复两个运行时错误：
1. `_extract_value_from_records` 中 SQL 查询结果包含 bytes 类型导致 JSON 序列化失败
2. `FileBasedProceduralRepository` 中文件名包含非法字符导致 Windows 写入失败

### 修改文件
- [x] tasks/capabilities/context_resolver/tree_context_resolver.py - 添加 `make_json_serializable()` 函数处理 bytes/datetime 等不可序列化类型
- [x] tasks/external/memory_store/filebased_procedural_repository.py - 添加 `_sanitize_filename()` 函数清理非法文件名字符

### Bug 1: JSON 序列化错误
**错误信息**: `Object of type bytes is not JSON serializable`

**原因**: SQL 查询返回的 BLOB/BINARY 字段是 bytes 类型，`json.dumps()` 无法序列化

**修复**: 添加递归处理函数，将 bytes 转为 UTF-8 字符串或 hex，datetime 转为 ISO 格式

### Bug 2: Windows 文件名错误
**错误信息**: `[Errno 22] Invalid argument: 'procedures_dev\<user_id:1,tenant_id:1>:marketing:...'`

**原因**: `node_scope` 格式包含 `<>:` 等 Windows 非法文件名字符

**修复**: 添加 `_sanitize_filename()` 函数，将 `<>:"/\|?*` 替换为下划线

### 状态
✅ 完成 (2026-01-19)

---
## [2026-01-19 已完成] - Connector 参数补全机制重构

### 任务描述
将语义指针补全逻辑从 LeafActor 下沉到 BaseConnector，实现统一的参数补全机制：
1. 在 BaseConnector 中实现 `_resolve_all_params()` 统一补全方法
2. DifyConnector 和 HttpConnector 调用统一方法
3. 移除 LeafActor 中的语义指针补全逻辑

### 修改文件
- [x] tasks/capabilities/excution/connect/base_connector.py - 新增 `_resolve_all_params()`、`_apply_semantic_pointers()`、`_is_id_like_param()`、`_get_known_params()` 方法
- [x] tasks/capabilities/excution/connect/dify_connector.py - 重构 `execute()` 调用统一补全方法
- [x] tasks/capabilities/excution/connect/http_connector.py - 重构 `execute()` 调用统一补全方法
- [x] tasks/common/messages/task_messages.py - 移除 `TaskMessage.semantic_pointers` 字段（不再需要在消息中传递）
- [x] tasks/agents/leaf_actor.py - 移除过渡性注释

### 关键决策
1. **统一补全入口**：所有参数补全都在 Connector 层完成
2. **四步补全流程**：预填充 → 描述增强 → 语义指针补全 → text_to_sql
3. **预留扩展点**：`_get_known_params()` 方法，后续可接入全局参数表
4. **移除冗余字段**：`TaskMessage.semantic_pointers` 不再需要，语义指针在 Connector 内部处理

### 补全流程
```
BaseConnector._resolve_all_params()
    │
    ├─ Step 1: pre_fill_known_params_with_llm()
    │          从 context 提取已有值
    │
    ├─ Step 2: enhance_param_descriptions_with_context()
    │          增强描述：activity_id → "租户 t_001 的活动ID"
    │
    ├─ Step 3: resolve_semantic_pointers()
    │          语义指针补全：→ "租户 t_001 昨天创建的双十一促销活动的ID"
    │
    └─ Step 4: resolve_context() (text_to_sql)
               使用精确描述查询数据库
```

### 状态
✅ 完成 (2026-01-19)

---
## [2026-01-19 已完成] - TaskRouter 重构为 Actor 模式

### 任务描述
将 TaskRouter 从普通类重构为 Thespian Actor，解决长时间任务（十分钟到小时级）的阻塞问题：
1. 当前 TaskRouter 用 `ask` 会阻塞 API 线程，用 `tell` 又收不到结果
2. 重构为 Actor 后可以异步接收 `TaskCompletedMessage`
3. API 只负责发消息并立即返回，结果通过 RabbitMQ 推送给前端

### 修改文件
- [x] tasks/router/task_router.py - 重构为 TaskRouterActor（继承 Actor）+ TaskRouterClient（同步包装器）
- [x] tasks/router/__init__.py - 更新导出，新增 TaskRouterActor、TaskRouterClient 等
- [x] tasks/entry_layer/api_server.py - API 改为异步模式，返回 202 Accepted
- [x] tasks/agents/leaf_actor.py - `_build_dify_running_config` 新增传递 `enriched_context` 和 `semantic_pointers`
- [x] tasks/capabilities/excution/connect/dify_connector.py - 新增语义指针支持，与 http_connector 保持一致

### 关键决策
1. **TaskRouterActor 继承 Actor**：可以通过 `receiveMessage` 接收 `TaskCompletedMessage`
2. **API 改为异步模式**：`/tasks/execute` 返回 202 Accepted，不等待结果
3. **结果统一通过 RabbitMQ 发布**：TaskRouterActor 收到完成消息后发布到 `task.result` 队列

### 架构变化
```
Before (阻塞模式):
API Server ──ask──► AgentActor ──► ... ──► LeafActor
     │                                         │
     └─────────────── 阻塞等待 ◄────────────────┘

After (异步模式):
API Server ──tell──► TaskRouterActor ──tell──► AgentActor ──► ... ──► LeafActor
     │                      │                                              │
     └── 立即返回 202       └◄──────── TaskCompletedMessage ◄──────────────┘
                            │
                            ▼
                      RabbitMQ (task.result)
                            │
                            ▼
                   Interaction ──► 前端 SSE
```

### 状态
✅ 完成 (2026-01-19)

---
## [2026-01-19 已完成] - TaskRouter 统一路由层 + NEED_INPUT 恢复机制 + RabbitMQ 结果回传

### 任务描述
1. 实现 tasks 服务的 `need_input` 恢复机制，支持任务暂停后通过补充参数恢复执行
2. 添加 `TaskRouter` 统一路由层，作为 tasks 服务的统一入口
3. 实现任务结果通过 RabbitMQ 回传给 interaction 服务，再通过 SSE 推送给前端

### 修改文件
- [x] tasks/external/repositories/task_state_repo.py - 新建 Redis 任务状态存储库
- [x] tasks/router/task_router.py - 新建统一任务路由层
- [x] tasks/router/__init__.py - 新建模块导出
- [x] tasks/external/message_queue/task_result_publisher.py - 新建 RabbitMQ 结果发布器
- [x] tasks/agents/leaf_actor.py - 添加 ResumeTaskMessage 处理，改用 Redis 保存状态
- [x] tasks/external/message_queue/rabbitmq_listener.py - 支持 TaskRouter 模式
- [x] tasks/external/message_queue/message_queue_factory.py - 支持 task_router 参数
- [x] tasks/entry_layer/api_server.py - 使用 TaskRouter，新增状态查询和取消接口
- [x] tasks/main.py - 启动时初始化 TaskRouter

### 关键决策
1. **TaskRouter 统一入口**：所有任务请求（API/RabbitMQ）都通过 TaskRouter 处理
2. **Redis 状态持久化**：任务状态保存到 Redis，支持进程重启后恢复
3. **LeafActor 恢复**：在 NEED_INPUT 时保存完整执行上下文到 Redis，恢复时加载并重新执行
4. **RabbitMQ 结果发布**：任务完成后发布到 `task.result` 队列，interaction 服务监听并推送 SSE

### 新增 API
- `GET /tasks/{task_id}/status` - 查询任务状态
- `POST /tasks/{task_id}/cancel` - 取消任务

### 数据流
```
新任务流程:
API/RabbitMQ → TaskRouter → AgentActor → TaskGroupAggregator → ResultAggregator → LeafActor → ExecutionActor
                                                                                      ↓
                                                                              (NEED_INPUT 时保存状态到 Redis)
                                                                                      ↓
TaskRouter._process_response() → 发布结果到 RabbitMQ (task.result)
                                                                                      ↓
interaction 服务 TaskResultListener → TaskResultHandler → SSE 推送给前端

恢复任务流程:
API/RabbitMQ (ResumeTask) → TaskRouter → 从 Redis 加载状态 → AgentActor → LeafActor._handle_resume_task()
                                                                              ↓
                                                                    合并参数，重新执行
```

### Redis 状态结构
```python
# key: flora:task:state:{task_id}
{
    "task_id": "xxx",
    "trace_id": "xxx",
    "task_path": "/agent_root/step_1",
    "status": "NEED_INPUT",
    "paused_at": "leaf",
    "missing_params": ["client_id", "amount"],
    "agent_id": "xxx",
    "original_content": "...",
    "original_description": "...",
    "global_context": {...},
    "enriched_context": {...},
    "parameters": {...},
    "leaf_state": {
        "agent_id": "xxx",
        "meta": {...},
        "dify_config": "...",
        "http_config": "...",
        "args_config": "..."
    }
}
```

### 状态
✅ 完成 (2026-01-19)

---
## [2026-01-16 19:30] - 语义指针补全功能实现

### 任务描述
实现语义指针补全功能，用于消解多层级 Agent 树中的代词歧义。系统沿树向上回溯父级 Agent 的业务记忆，将模糊的参数描述（如"该用户"、"他"）转化为精确的语义指针。

### 修改文件
- [x] tasks/capabilities/llm_memory/unified_manageer/manager.py - 新增 `get_ancestor_context()` 和 `build_ancestor_context_summary()` 方法
- [x] tasks/capabilities/context_resolver/tree_context_resolver.py - 新增 `resolve_semantic_pointers()`、`_detect_ambiguous_references()`、`_batch_resolve_ambiguities()`、`enhance_param_descriptions_with_semantic_pointers()` 方法
- [x] tasks/common/context/context_entry.py - 新增 `SemanticPointer` 数据类
- [x] tasks/common/messages/task_messages.py - TaskMessage 新增 `semantic_pointers` 字段
- [x] tasks/agents/leaf_actor.py - 新增 `_resolve_semantic_pointers_for_task()` 方法，在执行前进行语义指针补全
- [x] tasks/capabilities/excution/connect/http_connector.py - `_resolve_remaining_params()` 支持使用语义指针增强参数描述

### 关键决策
1. 模糊引用检测：使用正则表达式检测代词（他/她/它）、指示词（该/此/其）、指示性引用（该用户/当前订单）
2. 父级记忆回溯：最多回溯 3 层，收集对话历史、核心记忆、Agent 描述
3. LLM 批量解析：一次 LLM 调用处理所有模糊参数，减少 API 调用
4. 置信度机制：低于 0.5 的语义指针不使用，回退到原始描述
5. 降级策略：无父级上下文时使用当前上下文增强

### 核心流程
```
参数描述 → 模糊引用检测 → 父级记忆回溯 → LLM 语义对齐 → 语义指针生成
                ↓                              ↓
         无模糊引用 → 直接返回          无父级上下文 → 当前上下文增强
```

### 示例效果
```
Before: client_id = "该用户的ID"
After:  client_id = "昨天第二个需要退款资格检查的客户的ID" (confidence: 0.9)
```

### 状态
✅ 完成 (2026-01-16 19:30)

---
## [2026-01-16 18:00] - TreeContextResolver 智能数据提取优化

### 任务描述
优化 `tree_context_resolver.py` 中 Vanna SQL 查询结果的处理逻辑，当返回多行或多列数据时，使用 LLM 根据业务需求智能提取所需值。

### 修改文件
- [x] tasks/capabilities/context_resolver/tree_context_resolver.py - 新增 `_extract_value_from_records` 方法

### 关键决策
1. 快速路径优化：单行单列直接返回值，单列多行返回值列表，避免不必要的 LLM 调用
2. 复杂情况使用 LLM：多行多列时，根据业务描述智能提取
3. 降级策略：LLM 不可用时返回原始记录
4. 记录数限制：最多传递 20 条记录给 LLM，避免 prompt 过长

### 处理逻辑
```
SQL 查询结果
    ↓
├─ 单行单列 → 直接返回值
├─ 单列多行 → 返回值列表
└─ 多行多列 → LLM 智能提取
```

### 状态
✅ 完成 (2026-01-16 18:00)

---
## [2026-01-16 17:00] - Interaction 服务新增任务结果监听功能

### 任务描述
在 interaction 服务中新增 RabbitMQ 监听器，监听任务执行结果，收到消息后：
1. 根据 trace_id 找到对应的 session_id
2. 将任务结果存储到对话历史
3. 通过 SSE 推送通知前端

### 修改文件
- [x] interaction/external/database/dialog_state_repo.py - 新增 trace_session_mapping 表和相关方法
- [x] interaction/external/message_queue/task_result_listener.py - 新建 RabbitMQ 任务结果监听器
- [x] interaction/external/message_queue/__init__.py - 新建模块导出
- [x] interaction/services/task_result_handler.py - 新建任务结果处理服务
- [x] interaction/services/__init__.py - 新建模块导出
- [x] interaction/main.py - 集成任务结果监听器，添加 lifespan 管理
- [x] interaction/interaction_handler.py - 在任务提交后保存 trace_id -> session_id 映射

### 关键决策
1. 新建 trace_session_mapping 表存储 trace_id -> session_id 映射，支持按 session_id 索引
2. 使用独立线程运行 RabbitMQ 监听器，避免阻塞主事件循环
3. 通过 asyncio.run_coroutine_threadsafe 在同步回调中调度异步 SSE 推送
4. 消息格式：{"trace_id": "xxx", "status": "SUCCESS/FAILED", "result": "...", "error": "..."}

### 新增功能
- 监听 `task.result` 队列（可通过 TASK_RESULT_QUEUE 环境变量配置）
- 收到任务结果后自动推送 SSE 事件 `task_result` 到对应会话
- 支持通过 trace_id 查询 session_id

### 状态
✅ 完成 (2026-01-16 17:30)

---
## [2026-01-16 16:00] - Trigger 服务重构

### 任务描述
按照 openspec/changes/refactor-trigger-service/ 方案重构 Trigger 服务：
1. 清理旧版调度系统（dispatcher.py, cron_scheduler）
2. 修复硬编码（root_agent_id）
3. 完善 Repository 方法
4. 支持修改触发条件（新增 API）
5. 测试验证
6. 清理冗余代码

### 修改文件
- [x] trigger/drivers/schedulers/dispatcher.py - 删除旧版 TaskDispatcher
- [x] trigger/drivers/__init__.py - 移除 TaskDispatcher 导出
- [x] trigger/drivers/schedulers/__init__.py - 移除 TaskDispatcher 导出
- [x] trigger/main.py - 移除 TaskDispatcher 启动代码
- [x] trigger/services/schedule_scanner.py - 修复 get_root_agent_id 从数据库查询
- [x] trigger/external/db/repo.py - 添加 update/update_scheduled_task/reschedule_task/cancel_task 接口
- [x] trigger/external/db/impl/sqlalchemy_impl.py - 实现新增的 Repository 方法
- [x] trigger/entry/api/routes.py - 新增 PATCH/GET/POST API 端点
- [x] trigger/external/client/ - 删除空目录

### 关键决策
1. 保留 cron_scheduler（处理 CRON 类型任务定义），ScheduleScanner 处理 ScheduledTaskDB
2. get_root_agent_id 改为异步函数，从 TaskDefinitionDB.content 中读取
3. 新增 API 支持修改任务定义和调度任务，包含状态校验

### 新增 API
- `PATCH /api/v1/definitions/{def_id}` - 修改任务定义（CRON 表达式、loop_config、is_active）
- `GET /api/v1/definitions/{def_id}` - 获取单个任务定义
- `GET /api/v1/scheduled-tasks/{task_id}` - 获取单个调度任务
- `PATCH /api/v1/scheduled-tasks/{task_id}` - 修改调度任务（仅 PENDING 状态）
- `POST /api/v1/scheduled-tasks/{task_id}/reschedule` - 重新调度任务
- `POST /api/v1/scheduled-tasks/{task_id}/cancel` - 取消调度任务

### 状态
✅ 完成 (2026-01-16 16:30)

---
## [2026-01-16 15:30] - 多项 Bug 修复和功能完善

### 任务描述
修复会话列表、Memory 功能、环境变量加载等多个问题，并添加 Memory 编辑 UI。

### 修改文件
- [x] front/src/features/TaskSidebar/index.vue - 修复切换对话不生效（task.id 改用 session_id）；修复 tasks 服务未运行时会话列表为空
- [x] front/src/features/ResourcePanel/index.vue - 修复 userId 格式错误；添加 Memory 编辑/添加/删除 UI
- [x] interaction/main.py - 修复 sys.path 优先级，确保 interaction/common 优先于根目录 common/；添加 env 导入
- [x] tasks/main.py - 修复 sys.path 优先级；添加 env 导入
- [x] trigger/main.py - 修复 sys.path 优先级；添加 env 导入
- [x] interaction/entry_layer/api_server.py - 修复后台任务中 BackgroundTasks 不生效的问题，改用 asyncio.create_task + run_in_executor
- [x] interaction/capabilities/memory/mem0_memory.py - 修复 set_core_memory 的 update 调用参数错误；修复 list_core_memories 返回值重复添加 key 前缀

### 关键决策
1. 各服务入口将自身目录加入 sys.path 优先级最高，避免与根目录同名模块冲突
2. 后台任务内部不能使用 FastAPI 的 BackgroundTasks，改用 asyncio + 线程池
3. Memory 编辑 UI 使用 Teleport 弹窗，支持添加、编辑、删除操作
4. Mem0 的 update() 方法只接受字符串参数，不是字典

### 状态
✅ 完成 (2026-01-16 15:30)

---
## [2026-01-16 00:45] - 添加核心记忆自动提取功能

### 任务描述
在每次对话结束后，自动从对话历史中提取用户的核心记忆（身份信息、偏好、联系方式、目标等），并智能判断是新增还是更新已有记忆。

### 修改文件
- [x] interaction/capabilities/memory/interface.py - 新增 `extract_and_save_core_memories()` 接口方法
- [x] interaction/capabilities/memory/mem0_memory.py - 实现 `extract_and_save_core_memories()` 方法
- [x] interaction/entry_layer/api_server.py - 修改 `trigger_memory_extraction()` 调用新接口
- [x] front/src/api/rag.js - 修复 API 端口配置错误 (8000 → 8001)

### 关键决策
1. 将核心记忆提取逻辑封装到 `IMemoryCapability` 接口中，保持架构一致性
2. 使用单次 LLM 调用同时完成提取和合并判断，减少 API 调用次数
3. 核心记忆提取失败时降级到原有逻辑，不影响主流程
4. 后台异步执行，不影响用户对话响应时间

### 相关文档
- openspec/changes/add-core-memory-extraction/proposal.md
- openspec/changes/add-core-memory-extraction/design.md

### 状态
✅ 完成 (2026-01-16 00:45)

---
## [2026-01-16 00:15] - 修复 Neo4j 孤立关系导致的节点不存在警告

### 任务描述
修复 `node_service.py` 中出现的 "节点 xxx 不存在" 警告。问题原因是 Neo4j 中存在指向已删除节点的 HAS_CHILD 关系，导致查询返回不存在的节点 ID。

### 修改文件
- [x] tasks/external/repositories/agent_structure_repo.py - 修改 `get_agent_relationship` 方法，在 Cypher 查询中添加 `:Agent` 标签约束，确保只返回存在的 Agent 节点

### 关键决策
1. 在 Cypher 查询中使用 `(parent:Agent)` 和 `(child:Agent)` 标签约束，而不是在 Python 代码中过滤
2. 这样可以从源头避免返回孤立关系指向的不存在节点

### 状态
✅ 完成 (2026-01-16 00:15)

---
