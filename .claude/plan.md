# 语义指针补全功能设计方案

## 1. 需求概述

### 1.1 问题背景
在多层级 Agent 树中，子级任务经常包含模糊的代词引用（如"该用户"、"他"、"这个订单"），这些引用在局部上下文中无法解析。需要通过向上回溯父级 Agent 的业务记忆，将模糊引用转化为精确的"语义指针"。

### 1.2 目标
将空洞的变量名（如 `client_id`）转化为自包含的语义实体：
```
Pointer: client_id → "The ID of the second customer from yesterday who requires a refund qualification check."
```

这个语义指针包含足够的信息量，使得下游系统能仅凭此描述生成精确的 SQL 查询，无需再次回调上层。

## 2. 现有架构分析

### 2.1 关键组件

| 组件 | 位置 | 职责 |
|------|------|------|
| `UnifiedMemoryManager` | `tasks/capabilities/llm_memory/unified_manageer/manager.py` | 统一记忆管理，支持六类记忆的存储和检索 |
| `ShortTermMemory` | `tasks/capabilities/llm_memory/unified_manageer/short_term.py` | 短期对话历史，按 scope 存储 |
| `TreeContextResolver` | `tasks/capabilities/context_resolver/tree_context_resolver.py` | 上下文解析，参数描述增强，数据定位 |
| `TreeManager` | `tasks/agents/tree/tree_manager.py` | Agent 树结构管理，提供 `get_parent()`, `get_full_path()` |
| `TaskMessage` | `tasks/common/messages/task_messages.py` | 任务消息，包含 `global_context`, `enriched_context` |
| `AgentActor` | `tasks/agents/agent_actor.py` | 非叶子节点执行器，负责任务规划和分发 |
| `LeafActor` | `tasks/agents/leaf_actor.py` | 叶子节点执行器，负责实际任务执行 |

### 2.2 现有记忆 Scope 机制
```python
# AgentActor._build_memory_scope()
def _build_memory_scope(self, user_id, task_path):
    root_agent_id = self._extract_root_agent_id(task_path)
    return f"{user_id}:{root_agent_id}"  # 如 "user_123:root_agent"

# AgentActor._build_node_memory_scope()
def _build_node_memory_scope(self, user_id, task_path):
    return f"{user_id}:{root_agent_id}:{self.agent_id}"  # 如 "user_123:root_agent:child_agent"
```

### 2.3 现有上下文增强方法
`TreeContextResolver` 已有 `enhance_param_descriptions_with_context()` 方法，但仅使用当前层的 `current_inputs`，未向上回溯。

## 3. 设计方案

### 3.1 核心流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    语义指针补全流程                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 参数识别                                                    │
│     ├─ 从任务描述中提取待解析参数                               │
│     └─ 识别模糊引用（代词、指示词）                             │
│                                                                 │
│  2. 父级记忆回溯                                                │
│     ├─ 沿树向上遍历父级 Agent                                   │
│     ├─ 检索每级的业务记忆（对话历史 + 核心记忆）                │
│     └─ 收集相关上下文片段                                       │
│                                                                 │
│  3. 语义对齐与合成                                              │
│     ├─ LLM 将局部意图与父级记忆进行语义对齐                     │
│     ├─ 消解代词歧义                                             │
│     └─ 生成完整的语义描述                                       │
│                                                                 │
│  4. 语义指针生成                                                │
│     ├─ 构建自包含的语义指针                                     │
│     └─ 注入到 enriched_context 中传递给下游                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 数据结构设计

#### 3.2.1 SemanticPointer 结构
```python
@dataclass
class SemanticPointer:
    """语义指针：自包含的参数语义描述"""
    param_name: str           # 参数名，如 "client_id"
    original_desc: str        # 原始描述，如 "用户ID"
    resolved_desc: str        # 补全后的描述，如 "昨天第二个需要退款资格检查的客户的ID"
    source_agent_path: List[str]  # 信息来源的 Agent 路径
    confidence: float         # 置信度 (0-1)
    resolution_chain: List[str]   # 解析链，记录每级补全的信息
```

#### 3.2.2 扩展 ContextEntry
```python
# tasks/common/context/context_entry.py
class ContextEntry(BaseModel):
    # ... 现有字段 ...
    semantic_pointer: Optional[SemanticPointer] = None  # 新增
```

### 3.3 模块修改

#### 3.3.1 UnifiedMemoryManager 新增方法

```python
# tasks/capabilities/llm_memory/unified_manageer/manager.py

def get_ancestor_context(
    self,
    user_id: str,
    agent_id: str,
    tree_manager: 'TreeManager',
    max_levels: int = 3,
    query: str = ""
) -> List[Dict[str, Any]]:
    """
    沿树向上回溯，收集父级 Agent 的业务记忆

    Args:
        user_id: 用户ID
        agent_id: 当前 Agent ID
        tree_manager: 树管理器实例
        max_levels: 最大回溯层数
        query: 可选的查询关键词，用于相关性过滤

    Returns:
        List[Dict]: 每级父节点的上下文信息
        [
            {
                "agent_id": "parent_agent_1",
                "level": 1,  # 距离当前节点的层数
                "conversation_history": "...",
                "core_memory": "...",
                "agent_description": "..."
            },
            ...
        ]
    """
```

#### 3.3.2 TreeContextResolver 新增方法

```python
# tasks/capabilities/context_resolver/tree_context_resolver.py

def resolve_semantic_pointers(
    self,
    param_descriptions: Dict[str, str],
    current_context: Dict[str, Any],
    agent_id: str,
    user_id: str
) -> Dict[str, SemanticPointer]:
    """
    将模糊的参数描述转化为语义指针

    Args:
        param_descriptions: 参数名 -> 原始描述
        current_context: 当前任务上下文
        agent_id: 当前 Agent ID
        user_id: 用户 ID

    Returns:
        Dict[str, SemanticPointer]: 参数名 -> 语义指针
    """

def _detect_ambiguous_references(
    self,
    text: str
) -> List[str]:
    """
    检测文本中的模糊引用（代词、指示词等）

    Returns:
        List[str]: 检测到的模糊引用列表
    """

def _synthesize_semantic_pointer(
    self,
    param_name: str,
    original_desc: str,
    ancestor_contexts: List[Dict],
    current_context: Dict[str, Any]
) -> SemanticPointer:
    """
    使用 LLM 合成语义指针
    """
```

#### 3.3.3 AgentActor/LeafActor 集成

在任务执行前调用语义指针补全：

```python
# tasks/agents/leaf_actor.py

def _execute_leaf_logic(self, task: AgentTaskMessage, sender: ActorAddress):
    # ... 现有代码 ...

    # 新增：语义指针补全
    if task.parameters:
        from capabilities.context_resolver.tree_context_resolver import TreeContextResolver
        from capabilities import get_capability

        resolver = get_capability("tree_context_resolver", TreeContextResolver)

        # 提取参数描述（从 args_config 或 meta）
        param_descriptions = self._extract_param_descriptions()

        # 解析语义指针
        semantic_pointers = resolver.resolve_semantic_pointers(
            param_descriptions=param_descriptions,
            current_context={
                "content": task.content,
                "description": task.description,
                "global_context": task.global_context,
                "enriched_context": task.enriched_context
            },
            agent_id=self.agent_id,
            user_id=self.current_user_id
        )

        # 将语义指针注入到 enriched_context
        for param_name, pointer in semantic_pointers.items():
            task.enriched_context[f"__semantic_pointer__{param_name}"] = pointer
```

### 3.4 LLM Prompt 设计

#### 3.4.1 模糊引用检测 Prompt
```
你是一个语义分析器。请分析以下文本，识别其中的模糊引用（代词、指示词等）。

【文本】
{text}

【输出格式】
JSON 数组，包含所有模糊引用：
["该用户", "他", "这个", ...]

如果没有模糊引用，输出空数组 []
```

#### 3.4.2 语义指针合成 Prompt
```
你是一个语义消歧助手。请根据父级上下文，将模糊的参数描述转化为精确的语义描述。

【当前参数】
参数名: {param_name}
原始描述: {original_desc}

【当前任务上下文】
{current_context}

【父级业务记忆】（从近到远）
{ancestor_contexts}

【任务】
1. 分析原始描述中是否存在模糊引用（如"该用户"、"他"、"这个订单"）
2. 从父级记忆中找到对应的精确信息
3. 生成一个自包含的语义描述，使得仅凭此描述就能精确定位数据

【输出格式】
{{
    "resolved_desc": "完整的语义描述，包含所有必要的限定条件",
    "confidence": 0.0-1.0,
    "resolution_chain": ["从父级1获取的信息", "从父级2获取的信息", ...]
}}

【示例】
输入: param_name="client_id", original_desc="该用户的ID"
父级记忆: "任务目标：处理昨天的第二个客户的投诉"
输出: {{
    "resolved_desc": "昨天第二个需要处理投诉的客户的ID",
    "confidence": 0.9,
    "resolution_chain": ["父级任务目标：处理昨天的第二个客户的投诉"]
}}
```

### 3.5 配置项

```python
# tasks/capabilities/context_resolver/config.py

SEMANTIC_POINTER_CONFIG = {
    "max_ancestor_levels": 3,      # 最大回溯层数
    "min_confidence_threshold": 0.6,  # 最低置信度阈值
    "enable_ambiguity_detection": True,  # 是否启用模糊引用检测
    "fallback_to_original": True,  # 低置信度时是否回退到原始描述
    "cache_ttl_seconds": 300,      # 语义指针缓存时间
}
```

## 4. 实现步骤

### Phase 1: 基础设施
1. [ ] 在 `UnifiedMemoryManager` 中添加 `get_ancestor_context()` 方法
2. [ ] 创建 `SemanticPointer` 数据类
3. [ ] 扩展 `ContextEntry` 添加 `semantic_pointer` 字段

### Phase 2: 核心逻辑
4. [ ] 在 `TreeContextResolver` 中实现 `resolve_semantic_pointers()`
5. [ ] 实现 `_detect_ambiguous_references()` 模糊引用检测
6. [ ] 实现 `_synthesize_semantic_pointer()` LLM 合成逻辑

### Phase 3: 集成
7. [ ] 修改 `LeafActor._execute_leaf_logic()` 集成语义指针补全
8. [ ] 修改 `HttpConnector` 使用语义指针增强参数描述
9. [ ] 添加配置项和开关

### Phase 4: 测试与优化
10. [ ] 单元测试
11. [ ] 集成测试
12. [ ] 性能优化（缓存、并行）

## 5. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| LLM 调用延迟 | 任务执行变慢 | 1. 缓存语义指针 2. 仅对检测到模糊引用的参数调用 LLM |
| 父级记忆过多 | Prompt 过长 | 1. 限制回溯层数 2. 相关性过滤 3. 摘要压缩 |
| 语义消歧错误 | 查询错误数据 | 1. 置信度阈值 2. 低置信度时回退原始描述 3. 人工确认机制 |
| 循环依赖 | 系统死锁 | TreeManager 已有防环机制 |

## 6. 预期效果

### Before
```
参数: client_id
描述: "该用户的ID"
→ SQL: SELECT * FROM clients WHERE ... (无法确定条件)
```

### After
```
参数: client_id
语义指针: "昨天第二个需要退款资格检查的客户的ID"
→ SQL: SELECT id FROM clients
       WHERE DATE(created_at) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)
       AND requires_refund_check = 1
       ORDER BY created_at
       LIMIT 1 OFFSET 1
```
