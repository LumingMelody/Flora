## ADDED Requirements

### Requirement: 核心记忆自动提取

系统 SHALL 在每次对话结束后，自动从对话历史中提取用户的核心记忆信息。

#### Scenario: 提取用户身份信息
- **WHEN** 用户在对话中提到 "我是产品部的张三"
- **THEN** 系统应提取并存储 `{"用户姓名": "张三", "部门": "产品部"}`

#### Scenario: 提取用户联系方式
- **WHEN** 用户在对话中提到 "我的工作电话是 13800138000"
- **THEN** 系统应提取并存储 `{"工作电话": "13800138000"}`

#### Scenario: 提取用户偏好
- **WHEN** 用户在对话中表达 "我习惯用钉钉沟通"
- **THEN** 系统应提取并存储 `{"沟通偏好": "钉钉"}`

#### Scenario: 提取用户目标
- **WHEN** 用户在对话中说 "我最近在做用户增长项目"
- **THEN** 系统应提取并存储 `{"当前项目": "用户增长项目"}`

---

### Requirement: 核心记忆智能更新

系统 SHALL 在提取新记忆时，智能判断是新增还是更新已有记忆。

#### Scenario: 更新已有记忆
- **WHEN** 用户说 "我的电话换成 13900001111 了"
- **AND** 系统已存储 `{"工作电话": "13800138000"}`
- **THEN** 系统应更新为 `{"工作电话": "13900001111"}`

#### Scenario: 新增不冲突的记忆
- **WHEN** 用户说 "我的邮箱是 test@example.com"
- **AND** 系统未存储邮箱相关记忆
- **THEN** 系统应新增 `{"邮箱": "test@example.com"}`

---

### Requirement: 提取失败降级处理

系统 SHALL 在核心记忆提取失败时，降级到原有的对话记忆存储逻辑。

#### Scenario: LLM 调用失败
- **WHEN** LLM 服务不可用或返回异常
- **THEN** 系统应记录错误日志
- **AND** 继续执行原有的 `add_memory()` 逻辑存储对话文本

#### Scenario: JSON 解析失败
- **WHEN** LLM 返回的内容无法解析为有效 JSON
- **THEN** 系统应记录警告日志
- **AND** 继续执行原有的 `add_memory()` 逻辑存储对话文本

---

### Requirement: 异步后台执行

系统 SHALL 在后台异步执行核心记忆提取，不阻塞用户对话响应。

#### Scenario: 不影响响应时间
- **WHEN** 用户发送消息并收到响应
- **THEN** 核心记忆提取应在后台任务中执行
- **AND** 用户响应时间不受影响

---

## ADDED Requirements (Bug Fix)

### Requirement: 前端 API 端口配置正确

前端 API 配置 SHALL 使用正确的 Interaction 服务端口。

#### Scenario: 正确的 API 端口
- **WHEN** 前端调用 Memory 或 RAG API
- **THEN** 应使用 `http://localhost:8001/v1` 作为基础 URL
