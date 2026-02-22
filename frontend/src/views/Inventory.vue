<template>
  <div class="inventory">
    <div class="header">
      <h2>库存管理</h2>
      <el-button type="primary" @click="showCheckDialog = true">库存盘点</el-button>
    </div>
    <el-card>
      <el-form inline :model="searchForm">
        <el-form-item label="商品">
          <el-input v-model="searchForm.keyword" placeholder="商品名称/编码" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">搜索</el-button>
          <el-button @click="searchForm.keyword = ''; loadData()">重置</el-button>
        </el-form-item>
      </el-form>
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="product_code" label="商品编码" width="120" />
        <el-table-column prop="product_name" label="商品名称" />
        <el-table-column prop="quantity" label="当前库存" width="100" />
        <el-table-column prop="stock_min" label="库存下限" width="100" />
        <el-table-column prop="stock_max" label="库存上限" width="100" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStockStatus(row).type">{{ getStockStatus(row).text }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="180" />
      </el-table>
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @change="loadData"
        style="margin-top: 20px"
      />
    </el-card>

    <el-card style="margin-top: 20px">
      <template #header>
        <span>库存流水</span>
      </template>
      <el-table :data="logs" v-loading="logsLoading" stripe size="small">
        <el-table-column prop="product_name" label="商品" />
        <el-table-column prop="change_type" label="变动类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getLogType(row.change_type)">{{ row.change_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="变动数量" width="100" />
        <el-table-column prop="order_no" label="相关单号" width="150" />
        <el-table-column prop="created_at" label="时间" width="180" />
      </el-table>
    </el-card>

    <el-dialog v-model="showCheckDialog" title="库存盘点" width="600px">
      <el-form :model="checkForm" label-width="100px">
        <el-form-item label="商品">
          <el-select v-model="checkForm.product_id" placeholder="选择商品" style="width: 100%">
            <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="盘点数量">
          <el-input-number v-model="checkForm.quantity" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCheckDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCheck">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getInventory, getInventoryLogs, checkInventory } from '../api/modules/inventory'
import { getProducts } from '../api/modules/products'

const loading = ref(false)
const logsLoading = ref(false)
const tableData = ref([])
const logs = ref([])
const products = ref([])
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })
const searchForm = reactive({ keyword: '' })
const showCheckDialog = ref(false)
const checkForm = reactive({ product_id: null, quantity: 0 })

const getStockStatus = (row) => {
  if (row.quantity < row.stock_min) return { type: 'danger', text: '库存不足' }
  if (row.quantity > row.stock_max) return { type: 'warning', text: '库存过剩' }
  return { type: 'success', text: '正常' }
}

const getLogType = (type) => {
  const types = { purchase_in: 'success', sale_out: 'warning', adjust: 'info' }
  return types[type] || 'info'
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getInventory({ page: pagination.page, page_size: pagination.pageSize, keyword: searchForm.keyword })
    tableData.value = res.data.items || []
    pagination.total = res.data.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const loadLogs = async () => {
  logsLoading.value = true
  try {
    const res = await getInventoryLogs({ page: 1, page_size: 20 })
    logs.value = res.data.items || []
  } catch (e) {
    console.error(e)
  } finally {
    logsLoading.value = false
  }
}

const loadProducts = async () => {
  try {
    const res = await getProducts({ page: 1, page_size: 100 })
    products.value = res.data.items || []
  } catch (e) {
    console.error(e)
  }
}

const handleCheck = async () => {
  try {
    await checkInventory(checkForm)
    ElMessage.success('盘点成功')
    showCheckDialog.value = false
    loadData()
    loadLogs()
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  loadData()
  loadLogs()
  loadProducts()
})
</script>

<style scoped>
.inventory .header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.inventory h2 {
  margin: 0;
}
</style>
