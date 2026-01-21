# ERP XMind 对应接口清单（基于 erp-server.md）

## 说明
- 依据 `erp.xmind` 的四大体系与关键职责提炼需求。
- 仅列出 `erp-server.md` 中可直接对应的接口；缺口单列。
- 接口格式：`METHOD PATH` - 名称。

## 一、产品体系
需求要点：SKU 编码/资料、BOM/条码、定价、生命周期管理。

### 产品
- `POST /admin-api/erp/product/create` - 创建产品
- `PUT /admin-api/erp/product/update` - 更新产品
- `GET /admin-api/erp/product/get` - 获得产品
- `GET /admin-api/erp/product/page` - 获得产品分页
- `GET /admin-api/erp/product/simple-list` - 获得产品精简列表
- `GET /admin-api/erp/product/export-excel` - 导出产品 Excel
- `DELETE /admin-api/erp/product/delete` - 删除产品

### 产品单位
- `POST /admin-api/erp/product-unit/create` - 创建产品单位
- `PUT /admin-api/erp/product-unit/update` - 更新产品单位
- `GET /admin-api/erp/product-unit/get` - 获得产品单位
- `GET /admin-api/erp/product-unit/page` - 获得产品单位分页
- `GET /admin-api/erp/product-unit/simple-list` - 获得产品单位精简列表
- `GET /admin-api/erp/product-unit/export-excel` - 导出产品单位 Excel
- `DELETE /admin-api/erp/product-unit/delete` - 删除产品单位

### 产品分类
- `POST /admin-api/erp/product-category/create` - 创建产品分类
- `PUT /admin-api/erp/product-category/update` - 更新产品分类
- `GET /admin-api/erp/product-category/get` - 获得产品分类
- `GET /admin-api/erp/product-category/list` - 获得产品分类列表
- `GET /admin-api/erp/product-category/simple-list` - 获得产品分类精简列表
- `GET /admin-api/erp/product-category/export-excel` - 导出产品分类 Excel
- `DELETE /admin-api/erp/product-category/delete` - 删除产品分类

### 缺口
- BOM 管理、条码管理、价表/限价、产品生命周期状态（Normal/Promote/Clearance/EOL）。

## 二、销售体系
需求要点：报价、销售订单(SO)、发货通知单(DN)、退货授权单、对账/应收、客户维护。

### 客户
- `POST /admin-api/erp/customer/create` - 创建客户
- `PUT /admin-api/erp/customer/update` - 更新客户
- `GET /admin-api/erp/customer/get` - 获得客户
- `GET /admin-api/erp/customer/page` - 获得客户分页
- `GET /admin-api/erp/customer/simple-list` - 获得客户精简列表
- `GET /admin-api/erp/customer/getCustomerNameList` - 获得客户名称列表
- `GET /admin-api/erp/customer/export-excel` - 导出客户 Excel
- `DELETE /admin-api/erp/customer/delete` - 删除客户

### 销售订单（SO）
- `POST /admin-api/erp/sale-order/create` - 创建销售订单
- `PUT /admin-api/erp/sale-order/update` - 更新销售订单
- `PUT /admin-api/erp/sale-order/update-status` - 更新销售订单的状态
- `GET /admin-api/erp/sale-order/get` - 获得销售订单
- `GET /admin-api/erp/sale-order/page` - 获得销售订单分页
- `GET /admin-api/erp/sale-order/export-excel` - 导出销售订单 Excel
- `DELETE /admin-api/erp/sale-order/delete` - 删除销售订单

### 销售出库（发货/发货通知单）
- `POST /admin-api/erp/sale-out/create` - 创建销售出库
- `PUT /admin-api/erp/sale-out/update` - 更新销售出库
- `PUT /admin-api/erp/sale-out/update-status` - 更新销售出库的状态
- `GET /admin-api/erp/sale-out/get` - 获得销售出库
- `GET /admin-api/erp/sale-out/page` - 获得销售出库分页
- `GET /admin-api/erp/sale-out/export-excel` - 导出销售出库 Excel
- `DELETE /admin-api/erp/sale-out/delete` - 删除销售出库

### 销售退货（RMA）
- `POST /admin-api/erp/sale-return/create` - 创建销售退货
- `PUT /admin-api/erp/sale-return/update` - 更新销售退货
- `PUT /admin-api/erp/sale-return/update-status` - 更新销售退货的状态
- `GET /admin-api/erp/sale-return/get` - 获得销售退货
- `GET /admin-api/erp/sale-return/page` - 获得销售退货分页
- `GET /admin-api/erp/sale-return/export-excel` - 导出销售退货 Excel
- `DELETE /admin-api/erp/sale-return/delete` - 删除销售退货

### 应收/对账（收款单）
- `POST /admin-api/erp/finance-receipt/create` - 创建收款单
- `PUT /admin-api/erp/finance-receipt/update` - 更新收款单
- `PUT /admin-api/erp/finance-receipt/update-status` - 更新收款单的状态
- `GET /admin-api/erp/finance-receipt/get` - 获得收款单
- `GET /admin-api/erp/finance-receipt/page` - 获得收款单分页
- `GET /admin-api/erp/finance-receipt/export-excel` - 导出收款单 Excel
- `DELETE /admin-api/erp/finance-receipt/delete` - 删除收款单

### 销售/收款统计
- `GET /admin-api/erp/sale-statistics/summary` - 获得销售统计
- `GET /admin-api/erp/sale-statistics/order-time-summary` - 获得销售单时间段统计
- `GET /admin-api/erp/sale-statistics/time-summary` - 获得销售时间段统计
- `GET /admin-api/erp/finance-receipt-statistics/order-time-summary` - 收款单-时间段统计
- `GET /admin-api/erp/overview-statistics/summary` - 数据总览统计

### 缺口
- 报价单、合同管理、信用控制、渠道政策/控价、商机与线索、发货通知单独立建模。

## 三、供应链体系
需求要点：仓储、库存、盘点与差异调整、库存调拨、出入库作业。

### 仓库
- `POST /admin-api/erp/warehouse/create` - 创建仓库
- `PUT /admin-api/erp/warehouse/update` - 更新仓库
- `PUT /admin-api/erp/warehouse/update-default-status` - 更新仓库默认状态
- `GET /admin-api/erp/warehouse/get` - 获得仓库
- `GET /admin-api/erp/warehouse/page` - 获得仓库分页
- `GET /admin-api/erp/warehouse/simple-list` - 获得仓库精简列表
- `GET /admin-api/erp/warehouse/export-excel` - 导出仓库 Excel
- `DELETE /admin-api/erp/warehouse/delete` - 删除仓库

### 产品库存
- `GET /admin-api/erp/stock/get` - 获得产品库存
- `GET /admin-api/erp/stock/get-count` - 获得产品库存数量
- `GET /admin-api/erp/stock/page` - 获得产品库存分页
- `GET /admin-api/erp/stock/export-excel` - 导出产品库存 Excel

### 产品库存明细/出入库明细
- `GET /admin-api/erp/stock-record/get` - 获得产品库存明细
- `GET /admin-api/erp/stock-record/page` - 获得产品库存明细分页
- `GET /admin-api/erp/stock-record/export-excel` - 导出产品库存明细 Excel
- `GET /admin-api/erp/stock-record-statistics/time-summary` - 库存看板-出入库明细-时间段统计

### 库存调拨
- `POST /admin-api/erp/stock-move/create` - 创建库存调拨单
- `PUT /admin-api/erp/stock-move/update` - 更新库存调拨单
- `PUT /admin-api/erp/stock-move/update-status` - 更新库存调拨单的状态
- `GET /admin-api/erp/stock-move/get` - 获得库存调拨单
- `GET /admin-api/erp/stock-move/page` - 获得库存调拨单分页
- `GET /admin-api/erp/stock-move/export-excel` - 导出库存调拨单 Excel
- `DELETE /admin-api/erp/stock-move/delete` - 删除库存调拨单

### 库存盘点/检查（文档中标注为“库存调拨单”）
- `POST /admin-api/erp/stock-check/create` - 创建库存调拨单
- `PUT /admin-api/erp/stock-check/update` - 更新库存调拨单
- `PUT /admin-api/erp/stock-check/update-status` - 更新库存调拨单的状态
- `GET /admin-api/erp/stock-check/get` - 获得库存调拨单
- `GET /admin-api/erp/stock-check/page` - 获得库存调拨单分页
- `GET /admin-api/erp/stock-check/export-excel` - 导出库存调拨单 Excel
- `DELETE /admin-api/erp/stock-check/delete` - 删除库存调拨单

### 其它出入库
- `POST /admin-api/erp/stock-in/create` - 创建其它入库单
- `PUT /admin-api/erp/stock-in/update` - 更新其它入库单
- `PUT /admin-api/erp/stock-in/update-status` - 更新其它入库单的状态
- `GET /admin-api/erp/stock-in/get` - 获得其它入库单
- `GET /admin-api/erp/stock-in/page` - 获得其它入库单分页
- `GET /admin-api/erp/stock-in/export-excel` - 导出其它入库单 Excel
- `DELETE /admin-api/erp/stock-in/delete` - 删除其它入库单
- `POST /admin-api/erp/stock-out/create` - 创建其它出库单
- `PUT /admin-api/erp/stock-out/update` - 更新其它出库单
- `PUT /admin-api/erp/stock-out/update-status` - 更新其它出库单的状态
- `GET /admin-api/erp/stock-out/get` - 获得其它出库单
- `GET /admin-api/erp/stock-out/page` - 获得其它出库单分页
- `GET /admin-api/erp/stock-out/export-excel` - 导出其它出库单 Excel
- `DELETE /admin-api/erp/stock-out/delete` - 删除其它出库单

### 库存统计
- `GET /admin-api/erp/stock-statistics/summary` - 库存概览统计

### 缺口
- 需求计划/预测、MRP、请购单(PR)、盘点差异调整单、库存预占/FIFO 参数化管理。

## 四、采购体系
需求要点：供应商主档、采购订单(PO)、采购入库(GRN)、退货、结算/付款、三单匹配。

### 供应商
- `POST /admin-api/erp/supplier/create` - 创建供应商
- `PUT /admin-api/erp/supplier/update` - 更新供应商
- `GET /admin-api/erp/supplier/get` - 获得供应商
- `GET /admin-api/erp/supplier/page` - 获得供应商分页
- `GET /admin-api/erp/supplier/simple-list` - 获得供应商精简列表
- `GET /admin-api/erp/supplier/getSupplierNameList` - 获得供应商名称列表
- `GET /admin-api/erp/supplier/export-excel` - 导出供应商 Excel
- `DELETE /admin-api/erp/supplier/delete` - 删除供应商

### 采购订单（PO）
- `POST /admin-api/erp/purchase-order/create` - 创建采购订单
- `PUT /admin-api/erp/purchase-order/update` - 更新采购订单
- `PUT /admin-api/erp/purchase-order/update-status` - 更新采购订单的状态
- `GET /admin-api/erp/purchase-order/get` - 获得采购订单
- `GET /admin-api/erp/purchase-order/page` - 获得采购订单分页
- `GET /admin-api/erp/purchase-order/export-excel` - 导出采购订单 Excel
- `DELETE /admin-api/erp/purchase-order/delete` - 删除采购订单

### 采购入库（GRN）
- `POST /admin-api/erp/purchase-in/create` - 创建采购入库
- `PUT /admin-api/erp/purchase-in/update` - 更新采购入库
- `PUT /admin-api/erp/purchase-in/update-status` - 更新采购入库的状态
- `GET /admin-api/erp/purchase-in/get` - 获得采购入库
- `GET /admin-api/erp/purchase-in/page` - 获得采购入库分页
- `GET /admin-api/erp/purchase-in/export-excel` - 导出采购入库 Excel
- `DELETE /admin-api/erp/purchase-in/delete` - 删除采购入库

### 采购退货
- `POST /admin-api/erp/purchase-return/create` - 创建采购退货
- `PUT /admin-api/erp/purchase-return/update` - 更新采购退货
- `PUT /admin-api/erp/purchase-return/update-status` - 更新采购退货的状态
- `GET /admin-api/erp/purchase-return/get` - 获得采购退货
- `GET /admin-api/erp/purchase-return/page` - 获得采购退货分页
- `GET /admin-api/erp/purchase-return/export-excel` - 导出采购退货 Excel
- `DELETE /admin-api/erp/purchase-return/delete` - 删除采购退货

### 付款与结算
- `POST /admin-api/erp/finance-payment/create` - 创建付款单
- `PUT /admin-api/erp/finance-payment/update` - 更新付款单
- `PUT /admin-api/erp/finance-payment/update-status` - 更新付款单的状态
- `GET /admin-api/erp/finance-payment/get` - 获得付款单
- `GET /admin-api/erp/finance-payment/page` - 获得付款单分页
- `GET /admin-api/erp/finance-payment/export-excel` - 导出付款单 Excel
- `DELETE /admin-api/erp/finance-payment/delete` - 删除付款单
- `POST /admin-api/erp/account/create` - 创建结算账户
- `PUT /admin-api/erp/account/update` - 更新结算账户
- `PUT /admin-api/erp/account/update-default-status` - 更新结算账户默认状态
- `GET /admin-api/erp/account/get` - 获得结算账户
- `GET /admin-api/erp/account/page` - 获得结算账户分页
- `GET /admin-api/erp/account/simple-list` - 获得结算账户精简列表
- `GET /admin-api/erp/account/export-excel` - 导出结算账户 Excel
- `DELETE /admin-api/erp/account/delete` - 删除结算账户

### 记账凭证/凭证上传
- `POST /admin-api/erp/bookkeeping-voucher/create` - 创建ERP 记账凭证
- `PUT /admin-api/erp/bookkeeping-voucher/update` - 更新ERP 记账凭证
- `POST /admin-api/erp/bookkeeping-voucher/upload` - ERP 上传纸质单据
- `GET /admin-api/erp/bookkeeping-voucher/get` - 获得ERP 记账凭证
- `GET /admin-api/erp/bookkeeping-voucher/page` - 获得ERP 记账凭证分页
- `GET /admin-api/erp/bookkeeping-voucher/export-excel` - 导出ERP 记账凭证 Excel
- `DELETE /admin-api/erp/bookkeeping-voucher/delete` - 删除ERP 记账凭证

### 采购/付款统计
- `GET /admin-api/erp/purchase-statistics/summary` - 获得采购统计
- `GET /admin-api/erp/purchase-statistics/order-time-summary` - 获得采购单时间段统计
- `GET /admin-api/erp/purchase-statistics/time-summary` - 获得采购时间段统计
- `GET /admin-api/erp/finance-payment-statistics/order-time-summary` - 付款单-时间段统计
- `GET /admin-api/erp/finance-payment-statistics/time-summary` - 业绩看板-交易趋势-时间段统计
- `GET /admin-api/erp/finance-statistics/bill-time-summary` - 驾驶舱-付款收款单金额-时间段统计
- `GET /admin-api/erp/finance-statistics/dashboard-time-summary` - 财务看板-应收应付汇总表-时间段统计
- `GET /admin-api/erp/finance-statistics/time-summary` - 资金看板-时间段统计
- `GET /admin-api/erp/supplier-statistics/summary` - 获得供应商统计

### 缺口
- 询比价(RFQ)、合同管理、供应商绩效(QCDS)、请购单(PR)、发票与三单匹配(PO/GRN/Invoice)。
