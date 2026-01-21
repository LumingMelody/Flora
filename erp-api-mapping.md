# ERP 接口映射（erp.xmind -> api-docs.json）

## 说明
- 基于 `erp.xmind` 的四大体系（产品、销售、供应链、采购）以及关键单据/对象进行需求抽取。
- 仅从 `api-docs.json` 中匹配得到的现有接口；未匹配到的部分单独列为缺口。

## 产品体系
对应 XMind 关键词：SKU、BOM、条码、NPI、PRD/MRD、选品标准书。

### 产品
- POST `/admin-api/system/product/create` - 创建产品
- PUT `/admin-api/system/product/update` - 更新产品
- GET `/admin-api/system/product/get` - 获得产品
- GET `/admin-api/system/product/page` - 获得产品分页
- DELETE `/admin-api/system/product/delete` - 删除产品

### 文档（支撑 MRD/PRD/选品标准书等）
- POST `/admin-api/system/document/create` - 创建文档
- PUT `/admin-api/system/document/update` - 更新文档
- GET `/admin-api/system/document/get` - 获得文档
- GET `/admin-api/system/document/page` - 获得文档分页
- GET `/admin-api/system/document/export-excel` - 导出文档 Excel
- DELETE `/admin-api/system/document/delete` - 删除文档

## 组织与权限（支撑“核心岗位与职责”落地）
对应 XMind 关键词：产品/销售/供应链/采购等岗位体系。

### 用户
- POST `/admin-api/system/user/create` - 新增用户
- PUT `/admin-api/system/user/update` - 修改用户
- PUT `/admin-api/system/user/update-status` - 修改用户状态
- PUT `/admin-api/system/user/update-password` - 重置用户密码
- GET `/admin-api/system/user/get` - 获得用户详情
- GET `/admin-api/system/user/page` - 获得用户分页列表
- GET `/admin-api/system/user/export` - 导出用户
- POST `/admin-api/system/user/import` - 导入用户
- GET `/admin-api/system/user/get-import-template` - 获得导入用户模板
- GET `/admin-api/system/user/list-all-simple` - 获取用户精简信息列表
- GET `/admin-api/system/user/simple-list` - 获取用户精简信息列表
- GET `/admin-api/system/user/getAllByTenantId` - 根据企业ID获取当前企业下所有用户

### 角色
- POST `/admin-api/system/role/create` - 创建角色
- PUT `/admin-api/system/role/update` - 修改角色
- GET `/admin-api/system/role/get` - 获得角色信息
- GET `/admin-api/system/role/page` - 获得角色分页
- GET `/admin-api/system/role/export-excel` - 导出角色 Excel
- DELETE `/admin-api/system/role/delete` - 删除角色
- GET `/admin-api/system/role/list-all-simple` - 获取角色精简信息列表
- GET `/admin-api/system/role/simple-list` - 获取角色精简信息列表

### 岗位
- POST `/admin-api/system/post/create` - 创建岗位
- PUT `/admin-api/system/post/update` - 修改岗位
- GET `/admin-api/system/post/get` - 获得岗位信息
- GET `/admin-api/system/post/page` - 获得岗位分页列表
- GET `/admin-api/system/post/export` - 岗位管理
- DELETE `/admin-api/system/post/delete` - 删除岗位
- GET `/admin-api/system/post/list-all-simple` - 获取岗位全列表
- GET `/admin-api/system/post/simple-list` - 获取岗位全列表

### 部门
- POST `/admin-api/system/dept/create` - 创建部门
- PUT `/admin-api/system/dept/update` - 更新部门
- GET `/admin-api/system/dept/get` - 获得部门信息
- GET `/admin-api/system/dept/list` - 获取部门列表
- DELETE `/admin-api/system/dept/delete` - 删除部门
- GET `/admin-api/system/dept/list-all-simple` - 获取部门精简信息列表
- GET `/admin-api/system/dept/simple-list` - 获取部门精简信息列表
- GET `/admin-api/system/dept/syncMaterial` - 企微环境-同步部门信息和员工信息

### 权限与菜单
- POST `/admin-api/system/permission/assign-role-data-scope` - 赋予角色数据权限
- POST `/admin-api/system/permission/assign-role-menu` - 赋予角色菜单
- POST `/admin-api/system/permission/assign-user-role` - 赋予用户角色
- GET `/admin-api/system/permission/list-role-menus` - 获得角色拥有的菜单编号
- GET `/admin-api/system/permission/list-user-roles` - 获得管理员拥有的角色编号列表
- POST `/admin-api/system/menu/create` - 创建菜单
- PUT `/admin-api/system/menu/update` - 修改菜单
- GET `/admin-api/system/menu/get` - 获取菜单信息
- GET `/admin-api/system/menu/list` - 获取菜单列表
- DELETE `/admin-api/system/menu/delete` - 删除菜单
- GET `/admin-api/system/menu/list-all-simple` - 获取菜单精简信息列表
- GET `/admin-api/system/menu/simple-list` - 获取菜单精简信息列表

## 销售体系（缺口）
XMind 涉及：报价单、销售订单(SO)、发货通知单(DN)、退货授权单、对账/应收等。

- `api-docs.json` 未包含销售/客户/订单/发货/退货/对账相关接口。

## 供应链体系（缺口）
XMind 涉及：库存预占、仓储入库/出库、库存调整单、盘点、MRP/需求计划等。

- `api-docs.json` 未包含库存/仓储/盘点/MRP/库存调整相关接口。

## 采购体系（缺口）
XMind 涉及：供应商主档、请购单(PR)、采购订单(PO)、入库单(GRN)、发票/三单匹配等。

- `api-docs.json` 未包含供应商/采购/入库/发票/结算相关接口。
