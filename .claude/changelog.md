# Changelog

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
