# Tasks: 添加核心记忆自动提取功能

## 1. 修复前端 API 端口问题

- [ ] 1.1 修改 `front/src/api/rag.js` 中的 `INTERACTION_API_BASE_URL` 从 `8000` 改为 `8001`

## 2. 实现核心记忆提取逻辑

- [ ] 2.1 在 `interaction/entry_layer/api_server.py` 中创建 `extract_core_memories()` 辅助函数
  - 构建 LLM 提取 prompt
  - 调用 LLM 生成结构化 JSON
  - 解析并返回核心记忆列表

- [ ] 2.2 创建 `merge_core_memories()` 辅助函数
  - 获取用户现有核心记忆
  - 调用 LLM 判断新旧记忆的合并策略
  - 返回需要新增/更新的记忆列表

- [ ] 2.3 修改 `trigger_memory_extraction()` 函数
  - 在现有逻辑前调用 `extract_core_memories()`
  - 调用 `merge_core_memories()` 处理冲突
  - 使用 `set_core_memory()` 存储提取的记忆
  - 添加 try-except 降级处理
  - 保留原有的 `add_memory()` 调用

## 3. 测试验证

- [ ] 3.1 手动测试：发送包含个人信息的对话，验证核心记忆是否被提取
- [ ] 3.2 手动测试：发送更新信息的对话，验证记忆是否被正确更新
- [ ] 3.3 验证前端 Memory 标签页能正确显示核心记忆

## 4. 更新文档

- [ ] 4.1 更新 `.claude/changelog.md` 记录本次变更
