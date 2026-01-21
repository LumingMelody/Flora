# Tasks: Connector 参数补全机制重构

## Phase 1: BaseConnector 通用补全逻辑

### Task 1.1: 实现 BaseConnector._resolve_all_params()
- [ ] 在 `base_connector.py` 中新增 `_resolve_all_params()` 方法
- [ ] 实现四步补全流程：
  1. `pre_fill_known_params_with_llm()` - 从 context 提取已有值
  2. `enhance_param_descriptions_with_context()` - 增强描述
  3. `resolve_semantic_pointers()` - 语义指针补全
  4. `resolve_context()` - text_to_sql 查询
- [ ] 新增 `_get_known_params()` 扩展点（预留全局参数表）

### Task 1.2: 新增辅助方法
- [ ] `_apply_semantic_pointers()` - 将语义指针应用到描述
- [ ] `_is_id_like_param()` - 判断是否为 ID 类型参数（从 HttpConnector 提取）

## Phase 2: Connector 适配

### Task 2.1: 重构 DifyConnector
- [ ] 移除现有的参数补全逻辑（约 80 行）
- [ ] 调用 `_resolve_all_params()` 替代
- [ ] 保持 `_get_required_inputs()` 获取 Dify schema
- [ ] 测试验证

### Task 2.2: 重构 HttpConnector
- [ ] 移除 `_pre_fill_from_context()` 方法
- [ ] 移除 `_resolve_remaining_params()` 方法
- [ ] 调用 `_resolve_all_params()` 替代
- [ ] 测试验证

## Phase 3: LeafActor 清理

### Task 3.1: 移除语义指针逻辑
- [ ] 移除 `_resolve_semantic_pointers_for_task()` 方法
- [ ] 移除 `_execute_leaf_logic()` 中的语义指针处理代码
- [ ] 简化 `_build_dify_running_config()` - 移除 semantic_pointers 传递
- [ ] 简化 `_build_http_running_config()` - 移除 semantic_pointers 传递

### Task 3.2: 清理消息字段（可选）
- [ ] 评估是否移除 `TaskMessage.semantic_pointers` 字段
- [ ] 如果移除，更新相关引用

## Phase 4: 测试验证

### Task 4.1: 功能测试
- [ ] Dify Connector 参数补全测试
- [ ] HTTP Connector 参数补全测试
- [ ] 语义指针补全效果验证

### Task 4.2: 回归测试
- [ ] 现有任务执行流程不受影响
- [ ] NEED_INPUT 恢复机制正常工作

## 完成标准

- [ ] Dify Connector 能够使用语义指针补全
- [ ] HTTP Connector 功能不受影响
- [ ] LeafActor 中不再有语义指针补全逻辑
- [ ] 代码复用率提高，重复逻辑消除
