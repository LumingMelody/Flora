# Proposal: Connector 参数补全机制重构

## 概述

将语义指针补全逻辑从 LeafActor 下沉到 BaseConnector，实现统一的参数补全机制，使 Dify Connector 和 HTTP Connector 都能使用完整的四步补全流程。

## 问题背景

### 当前问题

1. **HTTP Connector**：参数 schema（args）在 Neo4j 节点的 `args` 属性中定义，LeafActor 可以提前获取并做语义指针补全
2. **Dify Connector**：参数 schema 需要调用 Dify API `/parameters` 才能获取，只有在 Connector 内部才知道
3. **结果**：语义指针补全在 LeafActor 层实现，但 Dify Connector 无法使用

### 期望效果

```
Before (activity_id):
  描述: "活动ID"
  → SQL 无法确定具体条件，可能返回多个结果

After (activity_id):
  第一步增强: "租户 t_001 的活动ID"
  第二步语义补全: "租户 t_001 昨天创建的双十一促销活动的ID"
  → SQL: SELECT id FROM activity WHERE tenant_id='t_001' AND name LIKE '%双十一%' AND DATE(created_at) = CURDATE() - 1
```

## 解决方案

### 架构变更

```
Before:
┌─────────────────────────────────────────────────────────────┐
│  LeafActor                                                  │
│    ├─ _resolve_semantic_pointers_for_task() ← 基于 args    │
│    └─ 传递 semantic_pointers 到 Connector                  │
├─────────────────────────────────────────────────────────────┤
│  HttpConnector                                              │
│    └─ 使用 semantic_pointers 增强描述                       │
├─────────────────────────────────────────────────────────────┤
│  DifyConnector                                              │
│    └─ ❌ 无法使用语义指针（schema 在这里才获取）            │
└─────────────────────────────────────────────────────────────┘

After:
┌─────────────────────────────────────────────────────────────┐
│  LeafActor                                                  │
│    └─ 只传递 context，不做语义指针补全                      │
├─────────────────────────────────────────────────────────────┤
│  BaseConnector                                              │
│    └─ _resolve_all_params() ← 统一的四步补全流程            │
│         ├─ 1. pre_fill_known_params_with_llm()              │
│         ├─ 2. enhance_param_descriptions_with_context()     │
│         ├─ 3. resolve_semantic_pointers()                   │
│         └─ 4. resolve_context() (text_to_sql)               │
├─────────────────────────────────────────────────────────────┤
│  HttpConnector / DifyConnector                              │
│    └─ 调用 _resolve_all_params()，传入各自的 schema         │
└─────────────────────────────────────────────────────────────┘
```

### 补全流程

```python
def _resolve_all_params(
    self,
    missing_params: Dict[str, str],      # {param_name: description}
    context: Dict[str, Any],              # enriched_context, global_context, etc.
    agent_id: str,
    user_id: str
) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """
    统一的参数补全流程

    Returns:
        (filled_params, still_missing_params)
    """
    # Step 1: 从 context 中直接提取已有值
    filled, remaining = pre_fill_known_params_with_llm(missing_params, context)

    # Step 2: 用 context 增强剩余参数的描述
    enhanced_descs = enhance_param_descriptions_with_context(remaining, context)

    # Step 3: 语义指针补全（消解歧义）
    semantic_pointers = resolve_semantic_pointers(enhanced_descs, context, agent_id, user_id)
    final_descs = apply_semantic_pointers(enhanced_descs, semantic_pointers)

    # Step 4: 使用精确描述查询数据库
    resolved = resolve_context(final_descs, agent_id)
    filled.update(resolved)

    # 检查仍然缺失的参数
    still_missing = {k: v for k, v in remaining.items() if k not in filled or not filled[k]}

    return filled, still_missing
```

## 影响范围

### 修改文件

| 文件 | 修改内容 |
|------|----------|
| `tasks/capabilities/excution/connect/base_connector.py` | 新增 `_resolve_all_params()` 统一补全方法 |
| `tasks/capabilities/excution/connect/dify_connector.py` | 调用 `_resolve_all_params()`，移除重复逻辑 |
| `tasks/capabilities/excution/connect/http_connector.py` | 调用 `_resolve_all_params()`，移除重复逻辑 |
| `tasks/agents/leaf_actor.py` | 移除 `_resolve_semantic_pointers_for_task()` 及相关逻辑 |

### 不修改

- `tasks/capabilities/context_resolver/tree_context_resolver.py` - 保持现有接口
- `tasks/common/messages/task_messages.py` - `semantic_pointers` 字段保留（可能后续移除）

## 扩展点

### 全局参数表（预留）

```python
def _get_known_params(self, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    获取已知参数（扩展点）

    后续可接入全局参数表，快速获取 tenant_id, user_id 等固定参数
    """
    # 当前实现：从 context 中提取
    known = {}
    for key in ("tenant_id", "user_id", "session_id"):
        if key in context.get("global_context", {}):
            known[key] = context["global_context"][key]
        elif key in context.get("enriched_context", {}):
            known[key] = context["enriched_context"][key]
    return known
```

## 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 补全逻辑变更导致现有功能异常 | 中 | 保持接口兼容，逐步迁移 |
| 性能影响（多次 LLM 调用） | 低 | 复用现有逻辑，无额外调用 |
| 语义指针补全失败 | 低 | 保留降级策略，失败时使用原始描述 |

## 验收标准

1. Dify Connector 能够使用语义指针补全
2. HTTP Connector 功能不受影响
3. LeafActor 中不再有语义指针补全逻辑
4. 补全流程统一，代码复用率提高
