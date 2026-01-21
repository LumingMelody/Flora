# Change: 重构 Trigger 服务

## Why

Trigger 服务需要完善以下核心功能：
1. **支持修改触发条件** - 当前无法修改 CRON 表达式、延迟时间、循环参数
2. **清理双重调度系统** - 新旧两套系统同时运行，逻辑混乱
3. **修复硬编码** - `get_root_agent_id()` 硬编码返回 "marketing"
4. **完善 Repository** - 缺少 `update_instance` 等方法，modify 操作会失败

## What Changes

### 1. 支持修改触发条件

新增/完善 API：
- `PATCH /api/v1/definitions/{def_id}` - 修改任务定义（CRON 表达式、循环配置等）
- `POST /api/v1/scheduled-tasks/{task_id}/reschedule` - 重新调度任务（修改执行时间）
- 完善 `PATCH /api/v1/traces/{trace_id}/modify` - 修改待执行任务的参数

### 2. 清理旧版调度系统
- **BREAKING**: 删除 `drivers/schedulers/dispatcher.py` (TaskDispatcher)
- 修改 `main.py` 移除旧版调度器启动
- ScheduleScanner 直接发送到 `worker.execute` 主题

### 3. 修复硬编码
- 实现 `get_root_agent_id()` 从 TaskDefinition 获取 agent_id
- TaskDefinition 添加 `root_agent_id` 字段

### 4. 完善 Repository
- 添加 `update_instance()` 方法
- 添加 `update_scheduled_task()` 方法
- 添加 `reschedule_task()` 方法

## Capabilities

### New Capabilities
- `modify-definition`: 修改任务定义的触发条件
- `reschedule-task`: 重新调度已创建的任务

### Modified Capabilities
- `trigger-scheduler`: 统一调度逻辑，移除旧版
- `trigger-repository`: 完善数据操作方法

## Impact

### 受影响的文件
- `trigger/entry/api/routes.py` - 新增/修改 API
- `trigger/services/lifecycle_service.py` - 完善 modify 逻辑
- `trigger/services/schedule_scanner.py` - 修复 get_root_agent_id，改用 worker.execute
- `trigger/external/db/impl/sqlalchemy_impl.py` - 完善 repository
- `trigger/external/db/models.py` - TaskDefinition 添加 root_agent_id
- `trigger/main.py` - 移除旧版调度器
- `trigger/drivers/schedulers/dispatcher.py` - 删除

### 数据库变更
- `task_definitions` 表添加 `root_agent_id` 字段
