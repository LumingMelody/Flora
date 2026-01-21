# Flora 项目使用与服务启动指南

## 项目结构概览
本项目由多个后端服务组成，前端在 `front/`。后端主要目录：
- `events/`：事件与观察服务（Event/Observer）
- `interaction/`：对话与任务交互服务
- `tasks/`：任务执行与 Agent 系统
- `trigger/`：调度与触发服务

## 环境准备
- Python 3.11（建议使用 `/usr/local/bin/python3`）
- Node.js（仅前端需要）
- 可选：Redis、RabbitMQ、PostgreSQL（见 `docker-compose.yml`）

启动基础依赖（可选）：
```bash
docker compose up -d
```

## 配置文件
- `events/` 会自动创建 `event_config.json`（默认端口 8000）。
- `trigger/` 会读取 `trigger_config.json`，不存在则使用默认值（服务端口默认 8001，数据库默认 sqlite）。
- `interaction/` 需要 `interaction_config.json`（能力配置，需自行准备）。

## 启动后端服务
建议在项目根目录运行，四个服务分别启动：

1) Events 服务（默认端口来自 `event_config.json`，默认 8000）
```bash
/usr/local/bin/python3 -m uvicorn events.main:app --host 0.0.0.0 --port 8000 --reload
```

2) Interaction 服务（默认端口 8000，注意避免与 Events 冲突）
```bash
/usr/local/bin/python3 -m uvicorn interaction.main:app --host 0.0.0.0 --port 8001 --reload
```

3) Tasks 服务（默认端口 8002）
```bash
/usr/local/bin/python3 tasks/main.py --host 0.0.0.0 --port 8002
```

4) Trigger 服务（默认端口 8001）
```bash
/usr/local/bin/python3 -m uvicorn trigger.main:app --host 0.0.0.0 --port 8003 --reload
```

提示：端口可按需调整，确保四个服务不冲突。

## 启动前端
```bash
cd front
npm install
npm run dev
```

## 健康检查
- Events: `GET /health`
- Trigger: `GET /health`

启动后如需联调，先确认四个服务都在各自端口监听，再打开前端页面。
