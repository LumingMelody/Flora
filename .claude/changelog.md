# Changelog

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
