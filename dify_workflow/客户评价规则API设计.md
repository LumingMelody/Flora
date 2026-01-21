# 客户评价规则 API 设计

## 概述

本文档定义了客户评价规则的存储和查询 API，用于支持 Dify Workflow 的规则创建和打标功能。

## 数据库表设计

### customer_evaluation_rule 表

```sql
CREATE TABLE customer_evaluation_rule (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    rule_name       VARCHAR(100) NOT NULL COMMENT '规则名称',
    industry        VARCHAR(100) NOT NULL COMMENT '适用行业',
    rule_content    JSON NOT NULL COMMENT '规则内容（JSON格式）',
    status          TINYINT DEFAULT 1 COMMENT '状态：0-禁用，1-启用',
    created_by      VARCHAR(48) COMMENT '创建人ID',
    tenant_id       VARCHAR(48) NOT NULL COMMENT '租户ID',
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_industry (industry),
    INDEX idx_tenant (tenant_id),
    INDEX idx_status (status)
) COMMENT '客户评价规则表';
```

### rule_content JSON 结构

```json
{
  "ruleName": "电商行业客户评价规则",
  "industry": "电商",
  "dimensions": [
    {
      "name": "客户价值",
      "weight": 0.3,
      "indicators": [
        {
          "name": "累计消费金额",
          "description": "客户历史总消费金额",
          "scoringCriteria": [
            {"range": ">=10000", "score": 100, "tag": "高价值客户"},
            {"range": "5000-9999", "score": 70, "tag": "中价值客户"},
            {"range": "<5000", "score": 30, "tag": "低价值客户"}
          ]
        }
      ]
    },
    {
      "name": "客户活跃度",
      "weight": 0.25,
      "indicators": [
        {
          "name": "最近访问天数",
          "description": "距离上次访问的天数",
          "scoringCriteria": [
            {"range": "<=7", "score": 100, "tag": "活跃客户"},
            {"range": "8-30", "score": 60, "tag": "一般客户"},
            {"range": ">30", "score": 20, "tag": "沉睡客户"}
          ]
        }
      ]
    }
  ],
  "tagDefinitions": [
    {"tagName": "高价值客户", "description": "消费能力强的优质客户", "priority": 1},
    {"tagName": "活跃客户", "description": "近期有互动的客户", "priority": 2},
    {"tagName": "流失风险", "description": "可能流失的客户", "priority": 3}
  ]
}
```

---

## API 接口定义

### 1. 创建评价规则

**POST** `/admin-api/scrm/customer-evaluation-rule/create`

#### 请求头
| Header | 类型 | 必填 | 说明 |
|--------|------|------|------|
| Authorization | string | 是 | Bearer {token} |
| tenant-id | string | 是 | 租户ID |
| Content-Type | string | 是 | application/json |

#### 请求体
```json
{
  "industry": "电商",
  "ruleName": "电商行业客户评价规则",
  "ruleContent": { ... },
  "createdBy": "user_123"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| industry | string | 是 | 行业名称 |
| ruleName | string | 是 | 规则名称 |
| ruleContent | object | 是 | 规则内容（JSON对象） |
| createdBy | string | 否 | 创建人ID |

#### 响应
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "id": 1,
    "ruleName": "电商行业客户评价规则",
    "industry": "电商",
    "createdAt": "2026-01-20T14:50:00Z"
  }
}
```

---

### 2. 获取评价规则

**GET** `/admin-api/scrm/customer-evaluation-rule/get`

#### 请求参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | long | 是 | 规则ID |

#### 请求头
| Header | 类型 | 必填 | 说明 |
|--------|------|------|------|
| Authorization | string | 是 | Bearer {token} |
| tenant-id | string | 是 | 租户ID |

#### 响应
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "id": 1,
    "ruleName": "电商行业客户评价规则",
    "industry": "电商",
    "ruleContent": { ... },
    "status": 1,
    "createdBy": "user_123",
    "createdAt": "2026-01-20T14:50:00Z",
    "updatedAt": "2026-01-20T14:50:00Z"
  }
}
```

---

### 3. 查询规则列表

**GET** `/admin-api/scrm/customer-evaluation-rule/list`

#### 请求参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| industry | string | 否 | 按行业筛选 |
| status | int | 否 | 按状态筛选 |
| pageNo | int | 否 | 页码，默认1 |
| pageSize | int | 否 | 每页数量，默认10 |

#### 响应
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "ruleName": "电商行业客户评价规则",
        "industry": "电商",
        "status": 1,
        "createdAt": "2026-01-20T14:50:00Z"
      }
    ],
    "total": 1
  }
}
```

---

### 4. 更新评价规则

**PUT** `/admin-api/scrm/customer-evaluation-rule/update`

#### 请求体
```json
{
  "id": 1,
  "ruleName": "电商行业客户评价规则V2",
  "ruleContent": { ... },
  "status": 1
}
```

#### 响应
```json
{
  "code": 0,
  "msg": "success",
  "data": true
}
```

---

### 5. 删除评价规则

**DELETE** `/admin-api/scrm/customer-evaluation-rule/delete`

#### 请求参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | long | 是 | 规则ID |

#### 响应
```json
{
  "code": 0,
  "msg": "success",
  "data": true
}
```

---

## 已有打标 API（参考）

### 单个客户打标

**POST** `/admin-api/scrm/customer-info/mark-tags`

```json
{
  "customerId": 123,
  "addTagIds": [1, 2, 3]
}
```

### 批量客户打标

**POST** `/admin-api/scrm/customer-info/mark-tags-batch`

```json
{
  "customerIds": [123, 456, 789],
  "tagIds": [1, 2, 3]
}
```

---

## 使用流程

```
┌─────────────────────────────────────────────────────────────┐
│                    Workflow 1: 创建规则                      │
├─────────────────────────────────────────────────────────────┤
│  输入: 行业名称                                              │
│    ↓                                                        │
│  LLM: 生成评价规则 (JSON)                                    │
│    ↓                                                        │
│  HTTP: POST /customer-evaluation-rule/create                │
│    ↓                                                        │
│  输出: rule_id                                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
                      保存 rule_id
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Workflow 2: 客户打标                      │
├─────────────────────────────────────────────────────────────┤
│  输入: rule_id + 客户信息 (JSON数组)                         │
│    ↓                                                        │
│  HTTP: GET /customer-evaluation-rule/get?id={rule_id}       │
│    ↓                                                        │
│  LLM: 根据规则评估客户，输出推荐标签                          │
│    ↓                                                        │
│  HTTP: POST /customer-info/mark-tags-batch                  │
│    ↓                                                        │
│  输出: 打标结果                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 客户信息输入格式示例

### 单个客户
```json
{
  "customerId": 123,
  "name": "张三",
  "totalSpent": 8500,
  "lastVisitDays": 5,
  "orderCount": 12,
  "avgOrderValue": 708
}
```

### 多个客户
```json
[
  {
    "customerId": 123,
    "name": "张三",
    "totalSpent": 8500,
    "lastVisitDays": 5
  },
  {
    "customerId": 456,
    "name": "李四",
    "totalSpent": 2000,
    "lastVisitDays": 45
  }
]
```
