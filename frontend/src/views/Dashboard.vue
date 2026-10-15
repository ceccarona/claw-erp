<template>
  <div class="dashboard">
    <h2>仪表盘</h2>
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" color="#409eff"><Goods /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.products }}</div>
              <div class="stat-label">商品数量</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" color="#67c23a"><Shop /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.suppliers }}</div>
              <div class="stat-label">供应商</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" color="#e6a23c"><User /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.customers }}</div>
              <div class="stat-label">客户</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" color="#f56c6c"><Box /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.inventory }}</div>
              <div class="stat-label">库存商品</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="low-stock-card">
          <div class="stat-card">
            <el-icon class="stat-icon" color="#f56c6c"><Warning /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.lowStock }}</div>
              <div class="stat-label">低库存预警</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card v-if="lowStockItems.length > 0" class="low-stock-alert">
          <template #header>
            <div style="display: flex; align-items: center; gap: 10px;">
              <el-icon color="#f56c6c"><Warning /></el-icon>
              <span>低库存商品预警</span>
              <el-tag type="danger" size="small">{{ lowStockItems.length }} 个商品</el-tag>
            </div>
          </template>
          <el-table :data="lowStockItems" size="small">
            <el-table-column prop="product_code" label="商品编码" width="120" />
            <el-table-column prop="product_name" label="商品名称" />
            <el-table-column label="当前库存" width="100">
              <template #default="{ row }">
                <el-tag type="danger" size="small">{{ row.quantity }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="stock_min" label="最低库存" width="100" />
            <el-table-column label="缺口" width="100">
              <template #default="{ row }">
                <span style="color: #f56c6c">{{ row.stock_min - row.quantity }}</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>最近采购订单</span>
          </template>
          <el-table :data="recentPurchases" size="small">
            <el-table-column prop="order_no" label="订单号" />
            <el-table-column prop="total_amount" label="金额" />
            <el-table-column prop="status" label="状态" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>最近销售订单</span>
          </template>
          <el-table :data="recentSales" size="small">
            <el-table-column prop="order_no" label="订单号" />
            <el-table-column prop="total_amount" label="金额" />
            <el-table-column prop="status" label="状态" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Goods, Shop, User, Box, Warning } from '@element-plus/icons-vue'
import { getProducts } from '../api/modules/products'
import { getSuppliers } from '../api/modules/suppliers'
import { getCustomers } from '../api/modules/customers'
import { getInventory, getLowStockItems } from '../api/modules/inventory'
import { getPurchases } from '../api/modules/purchases'
import { getSales } from '../api/modules/sales'

const stats = ref({
  products: 0,
  suppliers: 0,
  customers: 0,
  inventory: 0,
  lowStock: 0
})

const recentPurchases = ref([])
const recentSales = ref([])
const lowStockItems = ref([])

const loadData = async () => {
  try {
    const [pRes, sRes, cRes, iRes, lowRes, purRes, salRes] = await Promise.all([
      getProducts({ page: 1, page_size: 1 }),
      getSuppliers({ page: 1, page_size: 1 }),
      getCustomers({ page: 1, page_size: 1 }),
      getInventory({ page: 1, page_size: 1 }),
      getLowStockItems(),
      getPurchases({ page: 1, page_size: 5 }),
      getSales({ page: 1, page_size: 5 })
    ])
    stats.value.products = pRes.data.total || 0
    stats.value.suppliers = sRes.data.total || 0
    stats.value.customers = cRes.data.total || 0
    stats.value.inventory = iRes.data.total || 0
    stats.value.lowStock = lowRes.data.total || 0
    lowStockItems.value = lowRes.data.items || []
    recentPurchases.value = purRes.data.items || []
    recentSales.value = salRes.data.items || []
  } catch (e) {
    console.error(e)
  }
}

onMounted(loadData)
</script>

<style scoped>
.dashboard h2 {
  margin-bottom: 20px;
}
.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
}
.stat-icon {
  font-size: 48px;
}
.stat-value {
  font-size: 28px;
  font-weight: bold;
}
.stat-label {
  color: #999;
  font-size: 14px;
}
.low-stock-card {
  cursor: pointer;
}
.low-stock-alert :deep(.el-card__header) {
  background-color: #fef0f0;
  border-bottom: 1px solid #fde2e2;
}
</style>
