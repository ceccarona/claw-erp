# Claw ERP - 进销存管理系统规格说明书

## 1. 项目概述

**项目名称**: Claw ERP  
**项目类型**: Web 管理系统（前后端分离）  
**核心技术栈**: 
- 后端: Python Flask + SQLite
- 前端: Vue 3 + Vite + Element Plus
- API: RESTful API

**核心功能**: 进销存管理（采购、销售、库存、财务一体化管理）

---

## 2. 系统架构

### 2.1 技术架构

```
┌─────────────────────────────────────────────────┐
│                   前端 (Vue 3)                   │
│              Element Plus + Axios               │
└─────────────────────┬───────────────────────────┘
                      │ HTTP API (JSON)
┌─────────────────────▼───────────────────────────┐
│                  后端 (Flask)                     │
│              RESTful API + SQLite               │
└─────────────────────────────────────────────────┘
```

### 2.2 项目结构

```
claw-erp/
├── backend/
│   ├── app.py              # Flask 应用入口
│   ├── config.py           # 配置文件
│   ├── models.py           # 数据库模型
│   ├── routes/             # API 路由
│   │   ├── auth.py
│   │   ├── products.py
│   │   ├── suppliers.py
│   │   ├── customers.py
│   │   ├── purchases.py
│   │   ├── sales.py
│   │   └── inventory.py
│   └── utils/
├── frontend/
│   ├── src/
│   │   ├── api/            # API 请求封装
│   │   ├── components/     # 公共组件
│   │   ├── views/          # 页面视图
│   │   ├── router/         # 路由配置
│   │   ├── stores/         # Pinia 状态管理
│   │   └── styles/         # 全局样式
│   └── index.html
└── SPEC.md
```

---

## 3. 功能模块

### 3.1 基础模块

#### 3.1.1 用户认证
- 用户登录/登出
- JWT 令牌认证
- 密码加密存储

#### 3.1.2 系统管理
- 用户管理（管理员）
- 角色权限（待扩展）

### 3.2 主业务模块

#### 3.2.1 商品管理 (Products)
- 商品列表（分页、搜索、筛选）
- 商品新增/编辑/删除
- 商品分类管理
- 商品单位管理
- 库存上下限设置

#### 3.2.2 供应商管理 (Suppliers)
- 供应商列表
- 供应商新增/编辑/删除
- 供应商联系人
- 供应商联系方式

#### 3.2.3 客户管理 (Customers)
- 客户列表
- 客户新增/编辑/删除
- 客户信用额度
- 客户联系方式

#### 3.2.4 采购管理 (Purchasing)
- 采购订单创建
- 采购订单列表
- 采购入库（入库单）
- 采购退货
- 供应商对账

#### 3.2.5 销售管理 (Sales)
- 销售订单创建
- 销售订单列表
- 销售出库（出库单）
- 销售退货
- 客户对账

#### 3.2.6 库存管理 (Inventory)
- 实时库存查询
- 库存盘点
- 库存调拨
- 库存预警
- 库存流水账

#### 3.2.7 财务报表（简化版）
- 采购汇总表
- 销售汇总表
- 库存汇总表
- 利润统计

---

## 4. 数据库设计

### 4.1 核心表结构

#### users (用户表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| username | VARCHAR(50) | 用户名（唯一） |
| password_hash | VARCHAR(255) | 密码哈希 |
| nickname | VARCHAR(50) | 昵称 |
| role | VARCHAR(20) | 角色：admin/user |
| created_at | DATETIME | 创建时间 |

#### products (商品表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| code | VARCHAR(50) | 商品编码 |
| name | VARCHAR(100) | 商品名称 |
| category_id | INTEGER | 分类ID |
| unit_id | INTEGER | 单位ID |
| cost_price | DECIMAL(10,2) | 成本价 |
| sale_price | DECIMAL(10,2) | 销售价 |
| stock_min | INTEGER | 库存下限 |
| stock_max | INTEGER | 库存上限 |
| status | INTEGER | 状态：1启用/0禁用 |
| created_at | DATETIME | 创建时间 |

#### categories (商品分类)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | VARCHAR(50) | 分类名称 |
| parent_id | INTEGER | 父分类ID |

#### units (计量单位)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| name | VARCHAR(20) | 单位名称 |

#### suppliers (供应商)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| code | VARCHAR(50) | 供应商编码 |
| name | VARCHAR(100) | 供应商名称 |
| contact | VARCHAR(50) | 联系人 |
| phone | VARCHAR(20) | 电话 |
| address | VARCHAR(255) | 地址 |
| status | INTEGER | 状态 |

#### customers (客户)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| code | VARCHAR(50) | 客户编码 |
| name | VARCHAR(100) | 客户名称 |
| contact | VARCHAR(50) | 联系人 |
| phone | VARCHAR(20) | 电话 |
| address | VARCHAR(255) | 地址 |
| credit_limit | DECIMAL(10,2) | 信用额度 |
| status | INTEGER | 状态 |

#### purchase_orders (采购订单)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| order_no | VARCHAR(50) | 订单号 |
| supplier_id | INTEGER | 供应商ID |
| order_date | DATE | 订单日期 |
| total_amount | DECIMAL(10,2) | 总金额 |
| status | VARCHAR(20) | 状态：draft/confirmed/received/cancelled |
| remark | TEXT | 备注 |
| created_by | INTEGER | 创建人 |
| created_at | DATETIME | 创建时间 |

#### purchase_order_items (采购明细)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| order_id | INTEGER | 订单ID |
| product_id | INTEGER | 商品ID |
| quantity | DECIMAL(10,2) | 数量 |
| unit_price | DECIMAL(10,2) | 单价 |
| amount | DECIMAL(10,2) | 金额 |

#### sales_orders (销售订单)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| order_no | VARCHAR(50) | 订单号 |
| customer_id | INTEGER | 客户ID |
| order_date | DATE | 订单日期 |
| total_amount | DECIMAL(10,2) | 总金额 |
| status | VARCHAR(20) | 状态 |
| remark | TEXT | 备注 |
| created_by | INTEGER | 创建人 |
| created_at | DATETIME | 创建时间 |

#### sales_order_items (销售明细)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| order_id | INTEGER | 订单ID |
| product_id | INTEGER | 商品ID |
| quantity | DECIMAL(10,2) | 数量 |
| unit_price | DECIMAL(10,2) | 单价 |
| amount | DECIMAL(10,2) | 金额 |

#### inventory (库存表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| product_id | INTEGER | 商品ID |
| quantity | DECIMAL(10,2) | 当前库存 |
| updated_at | DATETIME | 更新时间 |

#### inventory_logs (库存流水)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| product_id | INTEGER | 商品ID |
| change_type | VARCHAR(20) | 变动类型 |
| quantity | DECIMAL(10,2) | 变动数量 |
| order_no | VARCHAR(50) | 相关单号 |
| created_at | DATETIME | 创建时间 |

---

## 5. API 接口设计

### 5.1 认证接口
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/me` - 获取当前用户

### 5.2 商品接口
- `GET /api/products` - 商品列表
- `POST /api/products` - 新增商品
- `PUT /api/products/:id` - 更新商品
- `DELETE /api/products/:id` - 删除商品

### 5.3 供应商接口
- `GET /api/suppliers` - 供应商列表
- `POST /api/suppliers` - 新增供应商
- `PUT /api/suppliers/:id` - 更新供应商
- `DELETE /api/suppliers/:id` - 删除供应商

### 5.4 客户接口
- `GET /api/customers` - 客户列表
- `POST /api/customers` - 新增客户
- `PUT /api/customers/:id` - 更新客户
- `DELETE /api/customers/:id` - 删除客户

### 5.5 采购接口
- `GET /api/purchases` - 采购订单列表
- `POST /api/purchases` - 创建采购订单
- `POST /api/purchases/:id/receive` - 采购入库

### 5.6 销售接口
- `GET /api/sales` - 销售订单列表
- `POST /api/sales` - 创建销售订单
- `POST /api/sales/:id/deliver` - 销售出库

### 5.7 库存接口
- `GET /api/inventory` - 库存列表
- `POST /api/inventory/check` - 库存盘点

---

## 6. 页面设计

### 6.1 页面结构
- 登录页
- 首页（仪表盘）
- 商品管理
- 供应商管理
- 客户管理
- 采购管理
- 销售管理
- 库存管理
- 财务报表

### 6.2 UI 设计
- 主题色: #1890ff（蓝色）
- 侧边栏导航
- 顶部 Header
- 内容区域使用 Element Plus 组件

---

## 7. 开发计划

### Phase 1: 基础框架搭建
- [x] 仓库创建
- [x] 项目结构初始化
- [ ] 后端：Flask + SQLite 基础架构
- [ ] 前端：Vue 3 + Vite + Element Plus 基础架构

### Phase 2: 核心功能开发
- [ ] 用户认证（登录/JWT）
- [ ] 商品管理 CRUD
- [ ] 供应商管理 CRUD
- [ ] 客户管理 CRUD

### Phase 3: 业务功能
- [ ] 采购订单/入库
- [ ] 销售订单/出库
- [ ] 库存管理
- [ ] 库存流水

### Phase 4: 报表与优化
- [ ] 财务报表
- [ ] 界面优化
- [ ] 部署准备

---

## 8. 验收标准

1. ✅ 用户可以登录系统
2. ✅ 可以进行商品增删改查
3. ✅ 可以进行供应商/客户管理
4. ✅ 可以创建采购订单并入库
5. ✅ 可以创建销售订单并出库
6. ✅ 库存实时更新
7. ✅ 库存流水可追溯
8. ✅ 基本的报表统计功能
