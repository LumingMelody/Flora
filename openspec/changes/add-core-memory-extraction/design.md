# Design: 核心记忆自动提取

## Context

Flora 系统已有完整的对话历史存储和 Mem0 记忆系统，但缺少从对话中主动提取结构化核心记忆的能力。现有的 `trigger_memory_extraction()` 函数只是将对话文本原样存入 Mem0，没有进行信息提取和结构化。

### 现有流程
```
对话结束 → trigger_memory_extraction() → add_memory(对话文本) → Mem0
```

### 目标流程
```
对话结束 → trigger_memory_extraction()
         → extract_core_memories(对话文本)  [新增]
         → merge_core_memories(新记忆, 旧记忆)  [新增]
         → set_core_memory(key, value)  [新增]
         → add_memory(对话文本)  [保留]
```

## Goals / Non-Goals

**Goals:**
- 自动从对话中提取用户核心信息（身份、偏好、联系方式等）
- 智能处理新旧记忆冲突（更新 vs 新增）
- 不影响现有对话响应性能
- 失败时优雅降级

**Non-Goals:**
- 不实现用户手动编辑记忆功能（已有 API）
- 不实现记忆的过期/清理机制
- 不实现跨用户的记忆共享

## Decisions

### Decision 1: 提取时机
**选择**: 每次对话结束后立即提取（后台异步）

**理由**:
- 复用现有的 `trigger_memory_extraction()` 后台任务机制
- 实时性好，用户下次对话即可使用新记忆
- 后台执行不影响用户体验

### Decision 2: LLM Prompt 设计
**选择**: 单次 LLM 调用，同时完成提取和合并判断

**Prompt 结构**:
```
你是一个记忆提取助手。请从对话中提取用户的核心信息。

【已有记忆】
{existing_memories}

【最近对话】
{conversation_text}

【任务】
1. 从对话中识别用户的核心信息（身份、偏好、联系方式、目标等）
2. 对比已有记忆，判断是新增还是更新
3. 返回 JSON 格式

【输出格式】
{
  "memories": [
    {"action": "add|update", "key": "记忆键", "value": "记忆值"}
  ]
}
```

**理由**:
- 减少 LLM 调用次数（成本和延迟）
- LLM 能更好地理解上下文进行合并判断

### Decision 3: 存储格式
**选择**: 使用现有的 `set_core_memory(user_id, key, value)` 接口

**理由**:
- 复用现有实现，无需修改 Mem0 集成
- key-value 格式便于前端展示和查询
- 与现有 API 兼容

### Decision 4: 错误处理
**选择**: 静默降级 + 日志记录

**理由**:
- 核心记忆提取是增强功能，失败不应影响主流程
- 原有的对话记忆存储仍然执行
- 日志便于问题排查

## Risks / Trade-offs

### Risk 1: LLM 提取质量
**风险**: LLM 可能提取不准确或遗漏重要信息
**缓解**:
- 设计清晰的 prompt 和示例
- 保留原始对话记忆作为补充

### Risk 2: API 成本增加
**风险**: 每次对话增加一次 LLM 调用
**缓解**:
- 后台异步执行，不影响用户体验
- 可后续增加节流控制（如 N 分钟内只提取一次）

### Risk 3: 记忆冲突误判
**风险**: LLM 可能错误地覆盖正确的旧记忆
**缓解**:
- Prompt 中强调"只有明确表示更新时才覆盖"
- 可后续增加记忆版本历史
