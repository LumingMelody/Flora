# Events 重构计划（详细版）

## 目标
- 重新定义 ID 语义，消除 request/trace/task 的歧义。
- 移除动态任务对 EventDefinition 的硬依赖，降低写放大。
- 保留 SignalService 作为 trace 生命周期控制平面，并为后续“每步运行参数”留接口。
- 数据模型与 API 对齐 1:N（request_id → trace_id）与 1:N（trace_id → task_id/instance_id）。

## 范围与边界
- 保留 Event/Observer 的职责边界与事件总线设计。
- SignalService 不降级，继续作为暂停/恢复/取消的唯一入口。
- 本次不改前端交互逻辑，仅修正后端语义与接口契约。

## 当前问题（摘要）
- `job_id` 与 `trace_id` 语义重叠，造成冗余与误用。
- 动态 DAG 也必须写 EventDefinition，导致不必要的写入。
- Lifecycle/Observer/AgentMonitor 假设“先定义再执行”，与动态任务冲突。

## 目标语义（ID 层级）
- **request_id**：业务意图层（前端请求锚点）。重试/分叉不变。
- **trace_id**：执行会话层（一次执行尝试）。**trace_id 在外部生成，Events 仅记录映射**。
- **task_id / instance_id**：原子节点层（DAG 节点）。运行时动态生成。
- **废弃 job_id**：以 trace_id 作为唯一会话 ID。

语义关系示意：
```
request_id
  ├─ trace_id A (第一次尝试)
  │    ├─ task_id 1
  │    ├─ task_id 2
  └─ trace_id B (重试)
       ├─ task_id 1
       ├─ task_id 3
```

## 数据模型重构（建议字段）
### EventTrace（新增）
- `trace_id`（PK）
- `request_id`（索引）
- `status`（RUNNING / FAILED / SUCCEEDED / CANCELED）
- `created_at` / `ended_at`
- `meta`（JSON，预留扩展）

### EventInstance（保留）
- `id`（task_id / instance_id）
- `trace_id`（FK）
- `definition_id`（可选，默认可空）
- `status` / `payload` / `started_at` / `ended_at`
- 删除 `job_id` 字段（或保留但不写入）

### EventDefinition（可选）
- 仅用于静态模板或预定义 agent 角色。

## API 调整（按现有路径补齐语义）
- **POST `/api/v1/traces/start`**
  - 入参：`request_id`（必填）+ `trace_id`（外部生成）+ `user_id` + `input_params`
  - 作用：记录 request_id ↔ trace_id 的映射，不在此生成 trace_id
- **POST `/api/v1/traces/events`**
  - 入参：`trace_id` + `task_id` + `status` + `payload`
  - 允许不提供 `definition_id`
- **GET `/api/v1/traces/latest-by-request/{request_id}`**
  - 返回：最新 trace_id
- **GET `/api/v1/traces/by-request/{request_id}`**
  - 返回：trace 列表（按 created_at 排序）
- **GET `/api/v1/traces/{trace_id}/tasks`**
  - 返回：该 trace 的节点列表
- **Signal 控制**
  - `/api/v1/traces/{trace_id}/cancel|pause|resume`

## 核心服务改造点
### LifecycleService
- `start_trace(request_id, trace_id)`：
  - 记录/更新 `EventTrace`（request_id ↔ trace_id）
  - **不负责生成 trace_id，不处理重试逻辑**
- `sync_execution_state`：
  - 直接写 `EventInstance`（definition 可空）
  - 仅依赖 `trace_id` + `task_id`

### ObserverService
- `get_trace_graph(trace_id)`：
  - 基于 `EventInstance` 构图
  - 无 definition 也可渲染

### AgentMonitorService
- 以 `trace_id` 汇总状态
- 使用 `task_id` 粒度记录节点健康

### SignalService
- 维持 trace 级控制能力
- 预留 `signal_payload` 或 `trace_meta` 用于存储每步运行参数

## 迁移策略（分阶段）
### Phase 1（兼容期）
- 新增 `EventTrace` 表
- `EventInstance` 保留 `job_id` 但停止写入
- 写入逻辑以 `trace_id` 为主

### Phase 2（切换期）
- 读路径全面改为 `trace_id`
- `definition_id` 允许为空

### Phase 3（清理期）
- 删除 `job_id` 字段
- 去除 definition-only 分支

## 向后兼容策略
- 保留 `latest-by-request` 查询
- 历史数据读取时将 `job_id` 映射到 `trace_id`
- 老 trace 可继续查询和展示

## 风险与对策
- **历史数据不可读**：加映射逻辑 + 迁移脚本回填。
- **重复 trace**：request_id 入口幂等处理。
- **图构建缺字段**：ObserverService 增加容错逻辑。

## 测试清单（详细）
- request_id 重试生成多个 trace_id
- 动态 task 不写 definition 也能被查询/渲染
- Signal pause/resume/cancel 仍有效
- trace status 汇总准确（成功/失败/取消）

## 交付物
- 模型调整与迁移脚本
- Lifecycle/Observer/AgentMonitor/Signal 改造
- API 文档与调用示例更新
