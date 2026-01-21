# Proposal: 草稿描述动态更新机制

**Change ID:** draft-description-dynamic-update
**Status:** IMPLEMENTED
**Created:** 2026-01-20
**Implemented:** 2026-01-20
**Author:** Claude

## Problem Statement

当前 TaskDraft 的 description 是在执行阶段通过简单拼接用户输入生成的，存在以下问题：

1. **描述质量差** - 直接拼接用户多轮对话，包含无关内容（"好的"、"嗯"）
2. **语义不连贯** - 用户修正了之前的说法，但拼接不会反映修正
3. **无法预览** - description 只在最后执行时生成，用户无法提前确认
4. **与槽位脱节** - 槽位变化后 description 没有同步更新

## Proposed Solution

为 TaskDraft 增加动态 description 更新机制：

- 在槽位变化时通过 LLM 自动生成高质量的任务描述
- 在状态变化（FILLING → PENDING_CONFIRM）时更新描述
- 静默更新，仅在最终确认时展示给用户
- LLM 失败时回退到原有拼接逻辑

## Key Requirements

1. 在 `TaskDraftDTO` 中新增 `description: Optional[str]` 字段
2. 槽位变化时触发 description 更新（单次 `update_draft_from_intent` 只触发一次）
3. 状态从 FILLING → PENDING_CONFIRM 时触发 description 更新
4. 使用 LLM 根据槽位+对话历史生成自然语言描述
5. 静默更新，仅在最终确认时展示给用户
6. LLM 调用失败时回退到原有的拼接逻辑

## Scope

### In Scope
- `TaskDraftDTO` 新增 `description` 字段
- `CommonTaskDraft` 新增 `_generate_description` 方法
- 修改 `update_draft_from_intent` 在末尾触发更新
- 修改 `set_draft_pending_confirm` 触发更新
- 失败降级处理

### Out of Scope
- 前端展示逻辑
- 用户手动编辑 description
- 防抖/延迟优化

## Key Scenarios

### Scenario 1: Happy Path - 多轮填槽
1. 用户说："帮我订一张明天去北京的机票"
2. 系统提取槽位：destination=北京, date=明天
3. LLM 生成 description："预订明天前往北京的机票"
4. 用户补充："下午的航班，经济舱"
5. 系统更新槽位：time=下午, class=经济舱
6. LLM 更新 description："预订明天下午前往北京的经济舱机票"
7. 进入 PENDING_CONFIRM，展示 description 给用户确认

### Scenario 2: 多槽位单次更新
1. 用户一句话包含多个信息："明天下午帮我订去北京的经济舱机票"
2. 一次意图识别提取 4 个槽位
3. 只调用一次 LLM 生成 description（不是 4 次）

### Scenario 3: LLM 失败降级
1. 用户填槽完成
2. 调用 LLM 生成 description 超时
3. 系统回退到拼接 `original_utterances` 的逻辑
4. 流程继续，不中断

## Technical Design

### 1. 数据模型变更

```python
# interaction/common/task_draft.py
class TaskDraftDTO(BaseModel):
    # ... existing fields ...

    # 新增：LLM 生成的任务描述
    description: Optional[str] = None
```

### 2. 核心方法

```python
# interaction/capabilities/task_draft_manager/common_task_draft_manager.py

def _generate_description(self, draft: TaskDraftDTO) -> str:
    """
    使用 LLM 根据槽位和对话历史生成任务描述

    Args:
        draft: 当前任务草稿

    Returns:
        生成的任务描述，失败时返回拼接的 utterances
    """
    # 1. 构建 prompt
    # 2. 调用 LLM
    # 3. 失败时降级到拼接逻辑
    pass

def _fallback_description(self, draft: TaskDraftDTO) -> str:
    """
    降级逻辑：拼接用户原始输入
    """
    user_utterances = [
        u for u in draft.original_utterances
        if not u.startswith("[系统补充信息]")
    ]
    return " ".join(user_utterances) if user_utterances else ""
```

### 3. 触发点

#### 触发点 1: `update_draft_from_intent` 末尾

```python
def update_draft_from_intent(self, draft, intent_result):
    # ... existing logic ...

    # 在返回前生成/更新 description
    draft.description = self._generate_description(draft)
    self.update_draft(draft)

    return { ... }
```

#### 触发点 2: `set_draft_pending_confirm`

```python
def set_draft_pending_confirm(self, draft):
    # 状态变化时确保 description 是最新的
    draft.description = self._generate_description(draft)
    draft.status = TaskDraftStatus.PENDING_CONFIRM
    self.draft_storage.save_draft(draft)
    return draft
```

### 4. 修改 `prepare_for_execution`

```python
def prepare_for_execution(self, draft):
    parameters = { ... }

    # 优先使用已生成的 description
    if "description" not in parameters:
        if draft.description:
            parameters["description"] = draft.description
        elif draft.original_utterances:
            parameters["description"] = self._fallback_description(draft)

    return parameters
```

## Affected Files

| File | Change Type | Description |
|------|-------------|-------------|
| `interaction/common/task_draft.py` | Modify | 新增 `description` 字段 |
| `interaction/capabilities/task_draft_manager/common_task_draft_manager.py` | Modify | 新增生成方法，修改触发点 |
| `interaction/capabilities/task_draft_manager/interface.py` | Optional | 可选：新增接口方法声明 |

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM 调用增加延迟 | 中 | 单次 intent 处理只调用一次；失败快速降级 |
| LLM 生成质量不稳定 | 低 | 可通过 prompt 优化；降级逻辑兜底 |
| 存储空间增加 | 低 | description 字段很小，影响可忽略 |

## Acceptance Criteria

- [ ] `TaskDraftDTO` 包含 `description: Optional[str]` 字段
- [ ] 槽位变化后 description 自动更新
- [ ] 状态变为 PENDING_CONFIRM 时 description 已生成
- [ ] LLM 失败时正确降级到拼接逻辑
- [ ] `prepare_for_execution` 优先使用已有 description
- [ ] 单次 `update_draft_from_intent` 只触发一次 LLM 调用
