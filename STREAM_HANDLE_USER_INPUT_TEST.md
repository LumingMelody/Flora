# stream_handle_user_input 测试流程

## 前置条件
- 本地服务可启动：`interaction/main.py`（默认端口 8001）。
- 前端可选：`front/`（用于验证 SSE 展示）。
- 数据库文件可写（对话历史存储）。

## 1) 启动后端
- 命令：`python3 interaction/main.py`
- 预期：终端看到 `Uvicorn running on http://0.0.0.0:8001`

## 2) 建立 SSE 监听（验证流式事件）
- 用 curl 直连 SSE：
  - `curl -N http://localhost:8001/v1/conversations/TSK-01/stream`
- 预期：保持长连接，等待事件。

## 3) 发送消息触发 stream_handle_user_input
- 另开终端 POST 消息：
  - `curl -X POST http://localhost:8001/v1/conversations/TSK-01/messages \
  -H 'Content-Type: application/json' \
  -H 'X-User-ID: 1' \
  -d '{"utterance":"你好","timestamp":1736410000,"metadata":{}}'`
- 预期：返回 `{"status":"accepted",...}`。

## 4) 观察 SSE 输出事件顺序
- 预期事件（可能包含）：
  - `event: thought`（含 `message` 字段）
  - `event: message`（逐字 `content`）
  - `event: meta`（会话元信息）
  - `event: done`
- 若无 `thought`，但有 `message`/`done`，依然属于正常流程。

## 5) 验证历史写入
- 查询历史：
  - `curl http://localhost:8001/v1/session/TSK-01/history?limit=20&offset=0`
- 预期：返回包含 `role/system` 的对话记录。

## 6) 前端联动验证（可选）
- 启动前端：`cd front && npm run dev`
- 选择会话 `TSK-01`，发送消息。
- 预期：
  - 先出现 “Working (Xs | esc to interrupt)” thinking 气泡
  - 再输出 AI 回复正文
  - 左侧会话列表可见（若已有会话数据）

## 常见问题排查
- SSE 无输出：确认 sessionId 一致（监听/发送同一 `TSK-01`）。
- 前端无思考气泡：确认 `front/src/features/Copilot/index.vue` 已更新。
- 无会话列表：确认后端 `/user/{user_id}/sessions` 已返回数据（日志或 curl 验证）。
