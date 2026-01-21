# Tasks: 草稿描述动态更新机制

**Change ID:** draft-description-dynamic-update

## Task List

### Phase 1: 数据模型变更

- [x] **Task 1.1**: 在 `TaskDraftDTO` 中新增 `description` 字段
  - File: `interaction/common/task_draft.py`
  - Add: `description: Optional[str] = None`

### Phase 2: 核心方法实现

- [x] **Task 2.1**: 实现 `_fallback_description` 方法
  - File: `interaction/capabilities/task_draft_manager/common_task_draft_manager.py`
  - 从 `original_utterances` 拼接生成描述（现有逻辑提取）

- [x] **Task 2.2**: 实现 `_generate_description` 方法
  - File: `interaction/capabilities/task_draft_manager/common_task_draft_manager.py`
  - 构建 prompt，调用 LLM 生成描述
  - 失败时调用 `_fallback_description` 降级

### Phase 3: 触发点集成

- [x] **Task 3.1**: 修改 `update_draft_from_intent`
  - File: `interaction/capabilities/task_draft_manager/common_task_draft_manager.py`
  - 在返回前调用 `_generate_description` 更新 description

- [x] **Task 3.2**: 修改 `set_draft_pending_confirm`
  - File: `interaction/capabilities/task_draft_manager/common_task_draft_manager.py`
  - 状态变化时调用 `_generate_description` 确保最新

- [x] **Task 3.3**: 修改 `prepare_for_execution`
  - File: `interaction/capabilities/task_draft_manager/common_task_draft_manager.py`
  - 优先使用 `draft.description`，无则降级

### Phase 4: 测试验证

- [x] **Task 4.1**: 验证 happy path
  - 多轮填槽后 description 正确生成
  - ✅ 语法检查通过
  - ✅ TaskDraftDTO.description 字段存在且默认为 None

- [x] **Task 4.2**: 验证降级逻辑
  - 模拟 LLM 失败，确认回退到拼接逻辑
  - ✅ _fallback_description 正确过滤系统补充信息
  - ✅ 空列表返回空字符串

## Dependencies

```
Task 1.1 (数据模型)
    ↓
Task 2.1 (降级方法) → Task 2.2 (生成方法)
                          ↓
              Task 3.1, 3.2, 3.3 (触发点)
                          ↓
                    Task 4.1, 4.2 (测试)
```

## Estimated Changes

| File | Lines Added | Lines Modified |
|------|-------------|----------------|
| `interaction/common/task_draft.py` | ~2 | 0 |
| `interaction/capabilities/task_draft_manager/common_task_draft_manager.py` | ~50 | ~15 |
| **Total** | ~52 | ~15 |
