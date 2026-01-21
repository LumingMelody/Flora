# Trigger 服务重构 - 详细设计

## 1. 当前架构问题

### 1.1 双重调度系统

```
当前 main.py 启动了 4 个后台任务：
┌─────────────────────────────────────────────────────────────┐
│  旧版系统（应删除）                                           │
│  ├─ cron_scheduler() - 旧版 CRON 调度                        │
│  └─ TaskDispatcher - 消费 task.execute，发送 worker.execute  │
├─────────────────────────────────────────────────────────────┤
│  新版系统（保留）                                             │
│  ├─ ScheduleScanner - 扫描数据库，发送 task.scheduled        │
│  └─ ScheduleDispatcher - 消费 task.scheduled/task.status    │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 消息主题混乱

| 主题 | 发送者 | 消费者 | 问题 |
|------|--------|--------|------|
| `task.scheduled` | ScheduleScanner | ScheduleDispatcher | ✅ 正常 |
| `task.execute` | LifecycleService | TaskDispatcher | ❌ 旧版，应删除 |
| `worker.execute` | TaskDispatcher | 无 | ❌ 无消费者 |
| `task.status_update` | 外部系统 | ScheduleDispatcher | ✅ 正常 |

### 1.3 数据流向（当前）

```
API 请求
    ↓
LifecycleService._core_dispatch()
    ├─ SchedulerService.schedule_*() → 创建 ScheduledTaskDB
    ├─ event_publisher.publish_start_trace() → HTTP → Events Service
    └─ [旧版] broker.publish_delayed("task.execute", ...) → 延迟消息
           ↓
    ┌──────┴──────┐
    ↓             ↓
ScheduleScanner   TaskDispatcher (旧版)
    ↓             ↓
task.scheduled    task.execute
    ↓             ↓
ScheduleDispatcher  → worker.execute (无消费者!)
    ↓
event_publisher.push_task_status()
    ↓
HTTP → Events Service
```

## 2. 目标架构

### 2.1 简化后的数据流

```
API 请求
    ↓
LifecycleService._core_dispatch()
    ├─ SchedulerService.schedule_*() → 创建 ScheduledTaskDB
    └─ event_publisher.publish_start_trace() → HTTP → Events Service
           ↓
ScheduleScanner (每 10 秒扫描)
    ├─ 查询 PENDING 且到期的任务
    ├─ 更新状态为 SCHEDULED
    └─ broker.publish("task.scheduled", msg)
           ↓
    ┌──────┴──────┐
    ↓             ↓
ScheduleDispatcher   Tasks 服务 (外部)
    ↓                    ↓
更新状态为 DISPATCHED    执行任务
    ↓                    ↓
push_task_status()   发送状态回调
    ↓                    ↓
HTTP → Events Service ←──┘
           ↓
task.status_update 消息
           ↓
ScheduleDispatcher._handle_status_update()
    ├─ 更新状态为 SUCCESS/FAILED
    └─ 如需重新调度，创建新 ScheduledTask
```

### 2.2 统一的消息主题

| 主题 | 发送者 | 消费者 | 用途 |
|------|--------|--------|------|
| `worker.execute` | ScheduleScanner | Tasks 服务 | 任务执行（外部通信） |
| `task.status_update` | Events 服务 | ScheduleDispatcher | 状态回调 |

**说明**：
- `worker.execute` 是 Tasks 服务实际消费的主题，保持不变
- ScheduleScanner 直接发送到 `worker.execute`，不再经过 TaskDispatcher 中转
- `task.scheduled` 可作为内部调度主题（可选保留）

### 2.3 完整的状态机

```
                    ┌─────────────┐
                    │   PENDING   │ (创建后初始状态)
                    └──────┬──────┘
                           │ ScheduleScanner 扫描到期任务
                           ↓
                    ┌─────────────┐
                    │  SCHEDULED  │ (已加入调度队列)
                    └──────┬──────┘
                           │ ScheduleDispatcher 分发
                           ↓
                    ┌─────────────┐
                    │ DISPATCHED  │ (已发送给执行系统)
                    └──────┬──────┘
                           │ Tasks 服务开始执行
                           ↓
                    ┌─────────────┐
                    │   RUNNING   │ (执行中) ← 新增状态
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           ↓               ↓               ↓
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │   SUCCESS   │ │   FAILED    │ │  CANCELLED  │
    └─────────────┘ └─────────────┘ └─────────────┘
```

## 3. 重构步骤

### Phase 1: 清理旧代码

1. **删除 `trigger/drivers/schedulers/dispatcher.py`**
   - 这是旧版 TaskDispatcher

2. **删除 `trigger/external/client/push_client.py`**
   - 功能已被 event_publisher.py 替代

3. **修改 `trigger/main.py`**
   - 移除 cron_scheduler() 启动
   - 移除 TaskDispatcher 启动
   - 只保留 ScheduleScanner 和 ScheduleDispatcher

### Phase 2: 统一消息主题

1. **修改 `trigger/services/lifecycle_service.py`**
   - 删除 `broker.publish_delayed("task.execute", ...)` 调用
   - 延迟任务通过 ScheduledTaskDB 的 scheduled_time 实现

2. **确认 Tasks 服务消费 `task.scheduled`**
   - 检查 tasks/external/message_queue/rabbitmq_listener.py

### Phase 3: 完善状态机

1. **修改 `trigger/common/enums.py`**
   ```python
   class TaskStatus(str, Enum):
       PENDING = "PENDING"
       SCHEDULED = "SCHEDULED"
       DISPATCHED = "DISPATCHED"
       RUNNING = "RUNNING"  # 新增
       SUCCESS = "SUCCESS"
       FAILED = "FAILED"
       CANCELLED = "CANCELLED"
   ```

2. **修改 `trigger/services/schedule_dispatcher.py`**
   - 添加 RUNNING 状态处理

### Phase 4: 修复硬编码

1. **修改 `trigger/services/schedule_scanner.py`**
   ```python
   def get_root_agent_id(definition_id: str, session) -> str:
       """从数据库查询 definition 对应的根节点 agent_id"""
       definition = await session.get(TaskDefinitionDB, definition_id)
       if definition and definition.content:
           content = json.loads(definition.content)
           return content.get("root_agent_id", "default")
       return "default"
   ```

## 4. 文件变更清单

### 删除的文件
- `trigger/drivers/schedulers/dispatcher.py`
- `trigger/external/client/push_client.py`
- `trigger/external/client/__init__.py` (如果为空)

### 修改的文件
- `trigger/main.py` - 移除旧版调度器
- `trigger/common/enums.py` - 添加 RUNNING 状态
- `trigger/services/lifecycle_service.py` - 移除旧版消息发送
- `trigger/services/schedule_scanner.py` - 修复 get_root_agent_id
- `trigger/services/schedule_dispatcher.py` - 添加 RUNNING 状态处理
- `trigger/drivers/__init__.py` - 移除 TaskDispatcher 导出

## 5. 风险评估

### 高风险
- Tasks 服务必须同时支持新消息格式，否则任务无法执行

### 中风险
- 状态机变更可能影响现有任务的状态查询

### 低风险
- 删除冗余代码不影响功能

## 6. 回滚方案

1. 保留旧代码的 git 提交
2. 如需回滚，恢复 dispatcher.py 和 main.py 的旧版启动逻辑
3. Tasks 服务保持同时消费新旧主题的能力
