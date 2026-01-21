# Design: Connector 参数补全机制重构

## 1. 整体架构

### 1.1 补全流程图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        BaseConnector._resolve_all_params()               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ Step 1: pre_fill_known_params_with_llm()                        │   │
│  │                                                                  │   │
│  │ Input:  missing_params = {activity_id: "活动ID"}                │   │
│  │         context = {tenant_id: "t_001", user_id: "u_001", ...}   │   │
│  │                                                                  │   │
│  │ Output: filled = {}  (没有直接匹配的值)                         │   │
│  │         remaining = {activity_id: "活动ID"}                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│                                    ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ Step 2: enhance_param_descriptions_with_context()               │   │
│  │                                                                  │   │
│  │ Input:  remaining = {activity_id: "活动ID"}                     │   │
│  │         context = {tenant_id: "t_001", ...}                     │   │
│  │                                                                  │   │
│  │ Output: enhanced = {activity_id: "租户 t_001 的活动ID"}         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│                                    ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ Step 3: resolve_semantic_pointers()                             │   │
│  │                                                                  │   │
│  │ Input:  enhanced = {activity_id: "租户 t_001 的活动ID"}         │   │
│  │         ancestor_context = "任务目标：处理昨天的双十一活动"      │   │
│  │                                                                  │   │
│  │ Output: semantic_pointers = {                                   │   │
│  │           activity_id: {                                        │   │
│  │             resolved_desc: "租户 t_001 昨天创建的双十一促销活动的ID",│
│  │             confidence: 0.9                                     │   │
│  │           }                                                     │   │
│  │         }                                                       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│                                    ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ Step 4: resolve_context() (text_to_sql)                         │   │
│  │                                                                  │   │
│  │ Input:  final_descs = {activity_id: "租户 t_001 昨天创建的..."}  │   │
│  │                                                                  │   │
│  │ SQL:    SELECT id FROM activity                                 │   │
│  │         WHERE tenant_id = 't_001'                               │   │
│  │         AND name LIKE '%双十一%'                                │   │
│  │         AND DATE(created_at) = CURDATE() - 1                    │   │
│  │                                                                  │   │
│  │ Output: resolved = {activity_id: "12345"}                       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 类图

```
┌─────────────────────────────────────────────────────────────┐
│                      BaseConnector                          │
├─────────────────────────────────────────────────────────────┤
│ + execute(inputs, params) -> Dict                           │
│ # _resolve_all_params(missing, context, agent_id, user_id)  │
│ # _get_known_params(context) -> Dict  [扩展点]              │
│ # _apply_semantic_pointers(descs, pointers) -> Dict         │
│ # _is_id_like_param(name, label) -> bool                    │
└─────────────────────────────────────────────────────────────┘
                              △
                              │
              ┌───────────────┴───────────────┐
              │                               │
┌─────────────────────────┐     ┌─────────────────────────┐
│     DifyConnector       │     │     HttpConnector       │
├─────────────────────────┤     ├─────────────────────────┤
│ + execute()             │     │ + execute()             │
│ - _get_required_inputs()│     │ - _check_missing_inputs()│
│   (调用 Dify API)       │     │   (使用 args_schema)    │
└─────────────────────────┘     └─────────────────────────┘
```

## 2. 核心实现

### 2.1 BaseConnector._resolve_all_params()

```python
def _resolve_all_params(
    self,
    missing_params: Dict[str, str],
    context: Dict[str, Any],
    agent_id: str,
    user_id: str
) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """
    统一的参数补全流程

    Args:
        missing_params: 缺失参数 {param_name: description}
        context: 上下文信息，包含：
            - global_context: 全局上下文
            - enriched_context: 富上下文
            - content: 任务内容
            - description: 任务描述
        agent_id: 当前 Agent ID
        user_id: 用户 ID

    Returns:
        (filled_params, still_missing_params)
    """
    if not missing_params:
        return {}, {}

    try:
        from ...context_resolver.interface import IContextResolverCapbility
        from ... import get_capability
        context_resolver: IContextResolverCapbility = get_capability(
            "context_resolver", IContextResolverCapbility
        )
    except Exception as e:
        logger.warning(f"Failed to get context_resolver: {e}")
        return {}, missing_params

    # Step 1: 从 context 中直接提取已有值
    filled_params, remaining_params = context_resolver.pre_fill_known_params_with_llm(
        base_param_descriptions=missing_params,
        current_context_str=context
    )
    logger.info(f"Step 1 - Pre-filled: {list(filled_params.keys())}, Remaining: {list(remaining_params.keys())}")

    if not remaining_params:
        return filled_params, {}

    # 判断是否全是 ID 类型参数（用于决定上下文增强策略）
    all_id_params = all(
        self._is_id_like_param(name, desc)
        for name, desc in remaining_params.items()
    )

    # 构建用于增强的上下文
    context_for_enhance = context
    if all_id_params:
        # ID 类型参数只使用关键字段，避免噪音
        safe_context = {}
        for key in ("user_id", "tenant_id", "userid", "session_id"):
            value = context.get("global_context", {}).get(key) or context.get("enriched_context", {}).get(key)
            if value:
                safe_context[key] = value
        context_for_enhance = safe_context or {"user_id": user_id}

    # Step 2: 用 context 增强剩余参数的描述
    enhanced_descs = context_resolver.enhance_param_descriptions_with_context(
        base_param_descriptions=remaining_params,
        current_inputs=context_for_enhance
    )
    logger.info(f"Step 2 - Enhanced descriptions: {enhanced_descs}")

    # Step 3: 语义指针补全（消解歧义）
    semantic_pointers = context_resolver.resolve_semantic_pointers(
        param_descriptions=enhanced_descs,
        current_context=context,
        agent_id=agent_id,
        user_id=user_id
    )
    final_descs = self._apply_semantic_pointers(enhanced_descs, semantic_pointers)
    logger.info(f"Step 3 - After semantic pointers: {final_descs}")

    # Step 4: 使用精确描述查询数据库
    resolved_params = context_resolver.resolve_context(final_descs, agent_id)
    logger.info(f"Step 4 - Resolved from DB: {resolved_params}")

    filled_params.update(resolved_params)

    # 检查仍然缺失的参数
    still_missing = {}
    for name, desc in remaining_params.items():
        value = filled_params.get(name)
        if value is None or (isinstance(value, str) and value.strip() == ""):
            still_missing[name] = desc

    return filled_params, still_missing
```

### 2.2 _apply_semantic_pointers()

```python
def _apply_semantic_pointers(
    self,
    descriptions: Dict[str, str],
    semantic_pointers: Dict[str, Dict[str, Any]]
) -> Dict[str, str]:
    """
    将语义指针应用到参数描述

    Args:
        descriptions: 原始描述 {param_name: description}
        semantic_pointers: 语义指针 {param_name: {resolved_desc, confidence, ...}}

    Returns:
        应用语义指针后的描述
    """
    result = {}
    for param_name, desc in descriptions.items():
        pointer = semantic_pointers.get(param_name)
        if pointer and isinstance(pointer, dict):
            confidence = pointer.get("confidence", 0)
            if confidence >= 0.5:  # 只使用置信度较高的语义指针
                resolved_desc = pointer.get("resolved_desc", desc)
                result[param_name] = resolved_desc
                logger.info(
                    f"[SemanticPointer] '{param_name}': '{desc}' -> '{resolved_desc}' "
                    f"(confidence: {confidence:.2f})"
                )
            else:
                result[param_name] = desc
        else:
            result[param_name] = desc
    return result
```

### 2.3 _get_known_params() 扩展点

```python
def _get_known_params(self, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    获取已知参数（扩展点）

    后续可接入全局参数表，快速获取固定参数

    Args:
        context: 上下文信息

    Returns:
        已知参数字典
    """
    known = {}
    global_ctx = context.get("global_context", {})
    enriched_ctx = context.get("enriched_context", {})

    # 常见的全局参数
    for key in ("tenant_id", "user_id", "session_id", "trace_id"):
        if key in global_ctx and global_ctx[key]:
            known[key] = global_ctx[key]
        elif key in enriched_ctx and enriched_ctx[key]:
            known[key] = enriched_ctx[key]

    return known
```

## 3. Connector 适配

### 3.1 DifyConnector.execute() 重构

```python
def execute(self, inputs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    # 1. 检查配置参数
    missing_config = self._check_missing_config_params(params)
    if missing_config:
        return {"status": "ERROR", "error": f"Missing config: {missing_config}"}

    # 2. 获取 Dify schema
    required_inputs = self._get_required_inputs(params)
    missing_inputs = self._check_missing_inputs(inputs, required_inputs)

    if missing_inputs:
        # 3. 构建上下文
        context = {
            "global_context": params.get("global_context", {}),
            "enriched_context": params.get("enriched_context", {}),
            "content": params.get("content", ""),
            "description": params.get("description", ""),
        }

        # 4. 调用统一补全方法
        filled, still_missing = self._resolve_all_params(
            missing_params=missing_inputs,
            context=context,
            agent_id=params.get("agent_id", ""),
            user_id=params.get("user_id", "")
        )

        # 5. 合并结果
        completed_inputs = {**inputs, **filled}

        if still_missing:
            return {
                "status": "NEED_INPUT",
                "missing": still_missing,
                "completed": completed_inputs
            }

        inputs = completed_inputs

    # 6. 调用 Dify API
    # ... 现有逻辑 ...
```

### 3.2 HttpConnector.execute() 重构

```python
def execute(self, inputs: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    # 1. 检查配置参数
    missing_config = self._check_missing_config_params(params)
    if missing_config:
        return {"status": "ERROR", "error": f"Missing config: {missing_config}"}

    args_schema = params.get("args_schema", [])

    if args_schema:
        missing_inputs = self._check_missing_inputs(inputs, args_schema)

        if missing_inputs:
            # 2. 构建上下文
            context = {
                "global_context": params.get("global_context", {}),
                "enriched_context": params.get("enriched_context", {}),
                "content": params.get("content", ""),
                "description": params.get("description", ""),
            }

            # 3. 调用统一补全方法
            filled, still_missing = self._resolve_all_params(
                missing_params=missing_inputs,
                context=context,
                agent_id=params.get("agent_id", ""),
                user_id=params.get("user_id", "")
            )

            # 4. 合并结果
            completed_inputs = {**inputs, **filled}

            if still_missing:
                return {
                    "status": "NEED_INPUT",
                    "missing": still_missing,
                    "completed": completed_inputs
                }

            inputs = completed_inputs

    # 5. 执行 HTTP 请求
    # ... 现有逻辑 ...
```

## 4. LeafActor 清理

### 4.1 移除的代码

```python
# 移除 _resolve_semantic_pointers_for_task() 方法（约 80 行）

# 移除 _execute_leaf_logic() 中的语义指针处理（约 15 行）
# Before:
semantic_pointers = self._resolve_semantic_pointers_for_task(task, args_config)
if semantic_pointers:
    for param_name, pointer_info in semantic_pointers.items():
        task.semantic_pointers[param_name] = SemanticPointer(...)

# After:
# 直接构建 ExecuteTaskMessage，不处理语义指针
```

### 4.2 简化 running_config 构建

```python
# _build_dify_running_config() 简化
def _build_dify_running_config(self, task: AgentTaskMessage, dify_api_key: str) -> Dict[str, Any]:
    return {
        "api_key": dify_api_key,
        "inputs": task.parameters,
        "agent_id": self.agent_id,
        "user_id": self.current_user_id,
        "content": str(task.content or ""),
        "description": str(task.description or ""),
        "global_context": task.global_context or {},
        "enriched_context": task.enriched_context or {},
        # 移除 semantic_pointers
    }

# _build_http_running_config() 简化
def _build_http_running_config(self, task: AgentTaskMessage, http_config: str, args_config: str) -> Dict[str, Any]:
    # ... 解析 http_config ...
    return {
        "url": url,
        "method": method,
        "args_schema": args_list,
        "agent_id": self.agent_id,
        "user_id": self.current_user_id,
        "content": str(task.content or ""),
        "description": str(task.description or ""),
        "inputs": task.parameters or {},
        "global_context": task.global_context or {},
        "enriched_context": task.enriched_context or {},
        # 移除 semantic_pointers
    }
```

## 5. 全局参数表扩展（后续）

### 5.1 设计思路

```python
class GlobalParamRegistry:
    """
    全局参数注册表

    维护任务链中的固定参数，避免重复查询
    """

    def __init__(self):
        self._params: Dict[str, Dict[str, Any]] = {}  # trace_id -> params

    def register(self, trace_id: str, params: Dict[str, Any]):
        """注册全局参数"""
        if trace_id not in self._params:
            self._params[trace_id] = {}
        self._params[trace_id].update(params)

    def get(self, trace_id: str, param_name: str) -> Optional[Any]:
        """获取全局参数"""
        return self._params.get(trace_id, {}).get(param_name)

    def get_all(self, trace_id: str) -> Dict[str, Any]:
        """获取所有全局参数"""
        return self._params.get(trace_id, {}).copy()

    def clear(self, trace_id: str):
        """清理全局参数"""
        self._params.pop(trace_id, None)
```

### 5.2 集成方式

```python
# BaseConnector._get_known_params() 扩展
def _get_known_params(self, context: Dict[str, Any]) -> Dict[str, Any]:
    known = {}

    # 1. 从全局参数表获取
    trace_id = context.get("trace_id")
    if trace_id:
        from ...registry import global_param_registry
        known.update(global_param_registry.get_all(trace_id))

    # 2. 从 context 补充
    # ... 现有逻辑 ...

    return known
```
