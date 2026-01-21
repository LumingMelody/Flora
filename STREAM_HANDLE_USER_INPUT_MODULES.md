# stream_handle_user_input 模块职责与验证点

> 目标：列出流程中涉及到的模块职责，并给出“能否正确执行”的验证方式。

## 1) API 层（SSE 入口与推送）
- 模块：`interaction/entry_layer/api_server.py`
- 职责：
  - 接收 `/conversations/{session_id}/messages` 请求，构造 `UserInputDTO`。
  - 异步调用 `process_and_push_events`，将 `stream_handle_user_input` 的 `yield` 推入 `SESSION_QUEUES`。
  - 提供 `/conversations/{session_id}/stream` SSE 流。
- 正确执行验证：
  - 发送 POST 后返回 `202 Accepted`。
  - SSE 流能收到 `event: thought|message|meta|done`。

## 2) 编排器（流式主流程）
- 模块：`interaction/interaction_handler.py` → `stream_handle_user_input`
- 职责：
  - 调用用户输入管理器，增强/规范用户输入。
  - 维护对话状态（DialogState）。
  - 意图识别与业务路由（闲聊/任务）。
  - 生成响应并流式 `yield`。
- 正确执行验证：
  - 日志出现 `Stage1 LLM Response` 或 “意图识别”相关提示。
  - SSE 能收到 `message`（字符流）与 `meta`。

## 3) 用户输入管理（输入增强）
- 模块：`interaction/capabilities/user_input_manager/common_user_input_manager.py`
- 职责：
  - 读取对话历史 + 长期记忆。
  - 调用 LLM 返回 `enhanced_utterance`。
  - 写入用户回合到上下文存储。
- 正确执行验证：
  - 日志中出现 `LLM Prompt` 与 JSON 输出。
  - `enhanced_utterance` 不会被改成“助手回复”。

## 4) 意图识别
- 模块：`interaction/capabilities/intent_recognition_manager/common_intent_recognition_manager.py`
- 职责：
  - 将输入识别为 `IDLE / CREATE / QUERY / ...`。
- 正确执行验证：
  - 日志出现 `Stage1 LLM Response: {'intent': ...}`。

## 5) 闲聊响应（IDLE Chat）
- 模块：`interaction/interaction_handler.py`（IDLE 分支）
- 职责：
  - 构造含历史的 prompt，调用 LLM 生成闲聊回复。
- 正确执行验证：
  - 日志出现闲聊 LLM 输出。
  - SSE 能流式输出 `message`。

## 6) 系统响应封装
- 模块：`interaction/capabilities/system_response_manager/common_system_response_manager.py`
- 职责：
  - 统一封装 `SystemResponseDTO`。
- 正确执行验证：
  - SSE `meta` 事件包含 `session_id / user_id`。

## 7) 上下文管理（对话历史）
- 模块：`interaction/capabilities/context_manager/common_context_manager.py`
- 职责：
  - 保存对话轮次 `DialogTurn`。
  - 提供按 session 查询历史。
- 正确执行验证：
  - `/session/{session_id}/history` 能取到最新回复。

## 8) 对话状态存储
- 模块：`interaction/external/database/dialog_state_repo.py`
- 职责：
  - 保存/读取 `DialogStateDTO`（session 层状态）。
- 正确执行验证：
  - `/session/{session_id}` 返回 name/description 等字段。

## 9) 会话列表
- 模块：`interaction/entry_layer/api_server.py` -> `/user/{user_id}/sessions`
- 职责：
  - 返回用户会话列表（供前端左侧列表）。
- 正确执行验证：
  - API 返回非空列表，包含 `session_id/name/description`。

## 10) 前端 SSE 订阅
- 模块：`front/src/composables/useApi.js`
- 职责：
  - 建立 EventSource，分发 `message/thought/meta/done`。
- 正确执行验证：
  - 浏览器 Network 中 SSE 连接稳定。
  - Console 不出现解析错误。

## 11) 前端展示（聊天流）
- 模块：`front/src/features/Copilot/index.vue`
- 职责：
  - 接收 `thought` 显示 “Working…” 气泡。
  - 接收 `message` 拼接正文。
- 正确执行验证：
  - 发送消息后先出现 thinking 气泡，再输出正文。

