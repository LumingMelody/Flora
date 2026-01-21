# Trigger 服务重构 - 任务清单

## Phase 1: 清理旧版调度系统

- [x] 1.1 删除 `trigger/drivers/schedulers/dispatcher.py`
- [x] 1.2 修改 `trigger/drivers/__init__.py` 移除 TaskDispatcher 导出
- [x] 1.3 修改 `trigger/main.py`
  - 移除 `TaskDispatcher` 启动
  - 保留 `ScheduleScanner` 和 `ScheduleDispatcher`
- [x] 1.4 修改 `trigger/services/schedule_scanner.py`
  - 将消息发送主题从 `task.scheduled` 改为 `worker.execute`

## Phase 2: 修复硬编码

- [x] 2.1 修改 `trigger/external/db/models.py`
  - TaskDefinitionDB 添加 `root_agent_id` 字段
- [x] 2.2 修改 `trigger/services/schedule_scanner.py`
  - 实现 `get_root_agent_id()` 从数据库查询
  - 添加 fallback 默认值
- [x] 2.3 数据库迁移脚本（如需要）

## Phase 3: 完善 Repository

- [x] 3.1 修改 `trigger/external/db/impl/sqlalchemy_impl.py`
  - 添加 `update_instance()` 方法
  - 添加 `update_scheduled_task()` 方法
  - 添加 `reschedule_task()` 方法
- [x] 3.2 修改 `trigger/external/db/repo.py`
  - 更新接口定义

## Phase 4: 支持修改触发条件

- [x] 4.1 新增 API: `PATCH /api/v1/definitions/{def_id}`
  - 支持修改 CRON 表达式
  - 支持修改 loop_config
  - 支持修改 is_active
  - 添加 CRON 表达式验证
- [x] 4.2 新增 API: `POST /api/v1/scheduled-tasks/{task_id}/reschedule`
  - 支持修改 scheduled_time
  - 支持修改 schedule_config
  - 只允许修改 PENDING 状态的任务
- [x] 4.3 完善 `PATCH /api/v1/traces/{trace_id}/modify`
  - 确保 repository 方法存在
  - 添加参数验证
- [x] 4.4 修改 `trigger/services/lifecycle_service.py`
  - 添加 `modify_definition()` 方法
  - 添加 `reschedule_task()` 方法

## Phase 5: 测试验证

- [x] 5.1 测试即时任务（IMMEDIATE）
- [x] 5.2 测试延迟任务（DELAYED）
- [x] 5.3 测试定时任务（CRON）
- [x] 5.4 测试循环任务（LOOP）
- [x] 5.5 测试修改 CRON 表达式
- [x] 5.6 测试重新调度任务
- [x] 5.7 测试任务取消/暂停/恢复

## Phase 6: 清理冗余代码（可选）

- [x] 6.1 删除 `trigger/external/client/push_client.py`（如未使用）
- [x] 6.2 统一导入路径
- [x] 6.3 添加缺失的日志记录
