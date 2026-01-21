# Change: 添加核心记忆自动提取功能

## Why

目前系统只是将对话文本存入 Mem0，但没有主动从对话中提取结构化的核心记忆（如用户身份、偏好、联系方式等），导致核心记忆列表为空，无法为用户提供个性化服务。

## What Changes

- 在 `trigger_memory_extraction()` 中增加 LLM 核心记忆提取逻辑
- 支持提取用户身份、偏好、目标、业务上下文、联系方式等信息
- 智能判断是新增还是更新已有记忆
- 失败时降级到原有逻辑
- **FIX**: 修复前端 API 端口配置错误 (8000 → 8001)

## Capabilities

### New Capabilities

- `memory-extraction`: 从对话历史中自动提取结构化核心记忆

### Modified Capabilities

- `memory`: 增强 `trigger_memory_extraction()` 函数，集成核心记忆提取

## Impact

### 代码影响
- `interaction/entry_layer/api_server.py` - 修改 `trigger_memory_extraction()` 函数
- `front/src/api/rag.js` - 修复 API 端口配置

### 依赖
- 需要 LLM 能力 (`ILLMCapability`)
- 需要 Memory 能力 (`IMemoryCapability`)

### 性能
- 每次对话后增加一次 LLM 调用（后台异步，不影响用户体验）
