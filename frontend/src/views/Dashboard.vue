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
import { Goods, Shop, User, Box } from '@element-plus/icons-vue'
import { getProducts } from '../api/modules/products'
import { getSuppliers } from '../api/modules/suppliers'
import { getCustomers } from '../api/modules/customers'
import { getInventory } from '../api/modules/inventory'
import { getPurchases } from '../api/modules/purchases'
import { getSales } from '../api/modules/sales'

const stats = ref({
  products: 0,
  suppliers: 0,
  customers: 0,
  inventory: 0
})

const recentPurchases = ref([])
const recentSales = ref([])

const loadData = async () => {
  try {
    const [pRes, sRes, cRes, iRes, purRes, salRes] = await Promise.all([
      getProducts({ page: 1, page_size: 1 }),
      getSuppliers({ page: 1, page_size: 1 }),
      getCustomers({ page: 1, page_size: 1 }),
      getInventory({ page: 1, page_size: 1 }),
      getPurchases({ page: 1, page_size: 5 }),
      getSales({ page: 1, page_size: 5 })
    ])
    stats.value.products = pRes.data.total || 0
    stats.value.suppliers = sRes.data.total || 0
    stats.value.customers = cRes.data.total || 0
    stats.value.inventory = iRes.data.total || 0
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
</style>
