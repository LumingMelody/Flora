# 记忆补全方案（先不改代码）

## 目标
- 用户输入“需要复制的活动ID”时，系统能自动补全为“取最近创建的活动ID（按 create_time 倒序取 1 条）”，并进入 Text-to-SQL 执行。

## 现状问题
- `llm_memory` 未启用，`AgentActor` 回退到 `NoopMemory`，上下文始终为空。
- 没有写入记忆的调用点，记忆系统即使启用也无法积累内容。
- 查询链路（MCP -> context_resolver -> text_to_sql）未使用记忆做语句补全。
- `UnifiedMemoryManager.add_memory_intelligently` 里存在 user_id 与能力名使用问题，可能导致写入失败。
- 规划与执行是不同 agent：记忆按 agent 维度检索时会失效，导致执行阶段查不到补全规则。

## 方案步骤（不改代码，仅明确方案）
1) 启用记忆能力
   - 在 `tasks/config.json` 中增加 `llm_memory` 配置（`active_impl=unified_memory`）。
   - 目标：`AgentActor` 不再使用 `NoopMemory`。

2) 明确需要修复的记忆实现问题
   - `tasks/capabilities/llm_memory/unified_manageer/manager.py`：
     - `add_memory_intelligently` 内部不应依赖未设置的 `self.user_id`，应使用传入的 `user_id`。
     - 获取 LLM 能力时不应写死 `"qwen"`，应使用系统默认 `"llm"`。
   - 目标：记忆真正写入到正确用户空间。

3) 设计写入点（每次用户输入都写入）
   - 在 `AgentActor` 处理用户输入后、规划前调用：
     - `memory_cap.add_memory_intelligently(user_id, user_input, metadata)`
   - 目标：让“需要复制的活动ID”进入记忆系统。

4) 记忆作用域调整（跨 agent 可命中）
   - 将记忆检索从“单 agent”改为“用户 + 业务域”：
     - 建议 scope = `user_id + ":" + root_agent_id`（root 来自 task_path 的首段）
     - 或更简单先用 `user_id` 全局 scope
   - 目标：执行阶段的 agent 也能命中同一份记忆规则。
   - 落点建议：
     - 优先方案：在 `TaskGroupAggregatorActor` 解析 `task_path` 首段并写入 `global_context["root_agent_id"]`（单点统一）。
     - 兜底方案：若上下文未带 root，则在 `MCPCapabilityActor` / `ExecutionActor` 中从 `task_path` 再解析一次。

5) 执行前补全（Late Binding）
   - 补全发生在执行链的最后一步：`ExecutionActor` 和 `MCPCapabilityActor` 都要做。
   - 执行前从 memory scope 取上下文，对 `description/content` 做 rewrite。
   - 目标：将“需要复制的活动ID”补全成“取最近创建的活动ID（create_time desc limit 1）”。

6) 记忆内容类型建议
   - 这类规则应写入 procedural memory（流程/默认规则）
   - 示例规则：复制活动默认来源=最近创建活动（按 create_time desc 取 1）

7) 验证与可观测性
   - 在 rewrite 点记录输入/输出日志（不含敏感信息）。
   - E2E 验证：
     - 输入“需要复制的活动ID”应被补全为“取最近创建的活动ID”。
     - SQL 生成应使用 `ORDER BY create_time DESC LIMIT 1`。

## 验收标准
- memory 启用后，`AgentActor` 不再打印 `llm_memory unavailable`。
- 输入“需要复制的活动ID”能稳定生成“最近创建活动ID”的 SQL。
- 全链路有可追踪日志，能看到补全前后文本变化。
