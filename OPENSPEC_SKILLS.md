# OpenSpec Skills 使用指南

OpenSpec 是一个**规范驱动开发**工具，核心思想是：**先明确要做什么，再写代码**。

## 工作流程图

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  /openspec:init │ ──▶ │/openspec:proposal│ ──▶ │ /openspec:apply │ ──▶ │/openspec:archive│
│   初始化项目     │     │   创建变更提案   │     │    实现变更      │     │   归档变更      │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
                                │                        │
                                ▼                        ▼
                        ┌───────────────┐        ┌───────────────┐
                        │/openspec:validate│      │ /openspec:show │
                        │   验证格式      │        │   查看详情     │
                        └───────────────┘        └───────────────┘
```

---

## Skills 详解

### 1. `/openspec:init` - 初始化项目

**用途**：在项目中创建 OpenSpec 目录结构

**创建的结构**：
```
openspec/
├── project.md          # 项目约定（技术栈、规范等）
├── specs/              # 规范目录（当前真实状态）
└── changes/            # 变更提案目录
    └── archive/        # 已完成的变更归档
```

**使用场景**：项目首次使用 OpenSpec 时

---

### 2. `/openspec:proposal <描述>` - 创建变更提案

**用途**：在写代码前，先创建一个结构化的变更提案

**创建的文件**：
```
openspec/changes/<change-id>/
├── proposal.md         # 为什么要改？改什么？
├── tasks.md            # 实现任务清单
├── design.md           # 技术设计（可选）
└── specs/              # 规范增量
    └── <capability>/
        └── spec.md     # 具体需求和场景
```

**示例**：
```
/openspec:proposal 添加用户双因素认证
```

**核心价值**：
- 明确 WHY（为什么要做）
- 明确 WHAT（要做什么）
- 定义验收标准（Scenarios）

---

### 3. `/openspec:apply <change-id>` - 实现变更

**用途**：按照已批准的提案，逐步实现任务

**工作流程**：
1. 读取 `proposal.md` 理解目标
2. 读取 `design.md` 理解技术方案
3. 读取 `specs/*.md` 理解需求
4. 按 `tasks.md` 逐个完成任务
5. 完成后标记 `- [ ]` → `- [x]`

**示例**：
```
/openspec:apply add-two-factor-auth
```

---

### 4. `/openspec:archive <change-id>` - 归档变更

**用途**：变更完成后，将提案归档并更新源规范

**操作**：
1. 验证所有任务已完成
2. 将 spec deltas 合并到 `openspec/specs/`
3. 移动变更到 `openspec/changes/archive/YYYY-MM-DD-<change-id>/`

**示例**：
```
/openspec:archive add-two-factor-auth
```

---

### 5. `/openspec:list` - 列出变更和规范

**用途**：查看当前所有活跃的变更和已有的规范

**输出示例**：
```
## Active Changes
| Change ID        | Status      | Description              |
|------------------|-------------|--------------------------|
| add-user-auth    | Ready       | 添加用户认证系统          |
| update-api       | In Progress | 更新 API 限流            |

## Specifications
| Capability | Requirements | Description    |
|------------|--------------|----------------|
| user-auth  | 3            | 用户认证和会话  |
```

---

### 6. `/openspec:show <item>` - 显示详情

**用途**：查看某个变更或规范的详细内容

**示例**：
```
/openspec:show add-user-auth    # 查看变更详情
/openspec:show user-auth        # 查看规范详情
```

**显示内容**：
- 变更：proposal、tasks 进度、design、spec deltas
- 规范：所有需求和场景

---

### 7. `/openspec:validate <item>` - 验证格式

**用途**：检查变更或规范的格式是否正确

**检查项**：
- 必需文件是否存在
- 需求格式是否正确 (`### Requirement:`)
- 场景格式是否正确 (`#### Scenario:`)
- 是否使用 SHALL/MUST
- 每个需求是否有场景

**示例**：
```
/openspec:validate add-user-auth
```

---

## 核心概念

### Spec 规范格式

```markdown
### Requirement: 用户登录
系统 SHALL 允许用户使用邮箱和密码登录。

#### Scenario: 登录成功
- **WHEN** 用户提供有效的邮箱和密码
- **THEN** 系统返回 JWT token

#### Scenario: 登录失败
- **WHEN** 用户提供无效的密码
- **THEN** 系统返回 401 错误
```

### Delta 增量操作

| 操作 | 用途 | 说明 |
|------|------|------|
| `## ADDED Requirements` | 新增需求 | 添加全新的功能需求 |
| `## MODIFIED Requirements` | 修改需求 | 需包含完整的更新内容 |
| `## REMOVED Requirements` | 删除需求 | 需说明原因和迁移方案 |
| `## RENAMED Requirements` | 重命名需求 | 使用 FROM:/TO: 格式 |

### Delta 示例

```markdown
## ADDED Requirements

### Requirement: 双因素认证
系统 MUST 在用户登录时要求第二因素验证。

#### Scenario: OTP 验证
- **WHEN** 用户提供有效凭据
- **THEN** 系统要求输入 OTP 验证码

## MODIFIED Requirements

### Requirement: 用户登录
系统 SHALL 允许用户使用邮箱和密码登录，并支持双因素认证。

#### Scenario: 登录成功（无 2FA）
- **WHEN** 用户提供有效凭据且未启用 2FA
- **THEN** 系统返回 JWT token

#### Scenario: 登录成功（有 2FA）
- **WHEN** 用户提供有效凭据且已启用 2FA
- **THEN** 系统要求 OTP 验证

## REMOVED Requirements

### Requirement: 旧版登录
**Reason**: 已被新版登录流程替代
**Migration**: 使用新的 /api/v2/auth/login 端点
```

---

## 目录结构说明

```
openspec/
├── project.md              # 项目约定（技术栈、编码规范等）
├── specs/                  # 当前真实状态 (Source of Truth)
│   ├── user-auth/
│   │   └── spec.md         # 用户认证规范
│   └── api-core/
│       └── spec.md         # API 核心规范
└── changes/                # 变更提案
    ├── add-two-factor/     # 活跃的变更
    │   ├── proposal.md
    │   ├── tasks.md
    │   ├── design.md
    │   └── specs/
    │       └── user-auth/
    │           └── spec.md # Delta 增量
    └── archive/            # 已完成的变更
        └── 2024-01-15-add-logging/
```

---

## 使用建议

| 场景 | 建议 |
|------|------|
| **新功能开发** | 先 `/openspec:proposal`，审批后 `/openspec:apply` |
| **Bug 修复** | 可以跳过 proposal，直接修复 |
| **代码重构** | 建议创建 proposal 明确范围 |
| **架构变更** | 必须创建 proposal，包含 design.md |
| **团队协作** | specs 是共享的真实状态，changes 是待审批的提案 |

### 何时需要 design.md

以下情况建议创建 `design.md`：
- 跨模块/服务的变更
- 引入新的外部依赖
- 重大数据模型变更
- 涉及安全、性能的复杂变更
- 需要迁移计划的变更

---

## 快速开始

```bash
# 1. 初始化 OpenSpec
/openspec:init

# 2. 创建变更提案
/openspec:proposal 添加用户认证功能

# 3. 查看变更列表
/openspec:list

# 4. 验证提案格式
/openspec:validate add-user-auth

# 5. 实现变更（审批后）
/openspec:apply add-user-auth

# 6. 归档完成的变更
/openspec:archive add-user-auth
```

---

## 参考资料

- [OpenSpec GitHub](https://github.com/Fission-AI/OpenSpec)
- [AGENTS.md 规范](https://agents.md/)
