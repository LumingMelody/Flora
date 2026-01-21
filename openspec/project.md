# Flora Project Conventions

## Overview
Flora 是一个分布式多智能体 AI 编排系统，包含 4 个独立的后端服务：
- **Events (8000)**: 中央事件中心
- **Interaction (8001)**: 用户对话、记忆管理
- **Tasks (8002)**: 多智能体执行
- **Trigger (8003)**: 定时任务调度

## Tech Stack
- **Backend**: Python, FastAPI, Thespian Actor Framework
- **Frontend**: Vue 3, Vite, TailwindCSS
- **Databases**: PostgreSQL, Neo4j, Redis, Chroma (向量存储)
- **External Services**: Dify (RAG), Mem0 (记忆), DashScope/Qwen (LLM)

## Conventions
- 使用中文注释和文档
- API 端点遵循 RESTful 风格
- 能力系统使用插件架构 (`capabilities/`)
- 配置通过环境变量和 JSON 配置文件管理

## Directory Structure
```
Flora/
├── interaction/     # 用户交互服务
├── tasks/           # 任务执行服务
├── trigger/         # 触发器服务
├── events/          # 事件服务
├── front/           # Vue 3 前端
└── openspec/        # 规格和变更提案
```
