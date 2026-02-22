<template>
  <div class="purchases">
    <div class="header">
      <h2>采购管理</h2>
      <el-button type="primary" @click="handleAdd">新建采购订单</el-button>
    </div>
    <el-card>
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="order_no" label="订单号" width="150" />
        <el-table-column prop="supplier_name" label="供应商" />
        <el-table-column prop="order_date" label="订单日期" width="120" />
        <el-table-column prop="total_amount" label="总金额" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'draft'" size="small" type="primary" @click="handleReceive(row)">入库</el-button>
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="800px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="供应商" prop="supplier_id">
          <el-select v-model="form.supplier_id" placeholder="请选择供应商" style="width: 100%">
            <el-option v-for="s in suppliers" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="订单日期" prop="order_date">
          <el-date-picker v-model="form.order_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="form.remark" type="textarea" />
        </el-form-item>
        <el-form-item label="商品明细">
          <el-table :data="form.items" border size="small">
            <el-table-column label="商品" width="200">
              <template #default="{ row, $index }">
                <el-select v-model="row.product_id" placeholder="选择商品" @change="onProductChange($index)">
                  <el-option v-for="p in products" :key="p.id" :label="p.name" :value="p.id" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="数量" width="120">
              <template #default="{ row }">
                <el-input-number v-model="row.quantity" :min="1" :precision="2" size="small" @change="calcAmount(row)" />
              </template>
            </el-table-column>
            <el-table-column label="单价" width="120">
              <template #default="{ row }">
                <el-input-number v-model="row.unit_price" :min="0" :precision="2" size="small" @change="calcAmount(row)" />
              </template>
            </el-table-column>
            <el-table-column label="金额">
              <template #default="{ row }">
                {{ row.amount?.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="60">
              <template #default="{ $index }">
                <el-button type="danger" size="small" @click="form.items.splice($index, 1)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-button type="primary" size="small" @click="addItem" style="margin-top: 10px">添加商品</el-button>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPurchases, createPurchase, updatePurchase, deletePurchase, receivePurchase } from '../api/modules/purchases'
import { getSuppliers } from '../api/modules/suppliers'
import { getProducts } from '../api/modules/products'

const loading = ref(false)
const tableData = ref([])
const suppliers = ref([])
const products = ref([])
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })

const dialogVisible = ref(false)
const dialogTitle = ref('')
const formRef = ref()
const form = reactive({
  id: null,
  supplier_id: null,
  order_date: '',
  remark: '',
  items: []
})

const rules = {
  supplier_id: [{ required: true, message: '请选择供应商', trigger: 'change' }],
  order_date: [{ required: true, message: '请选择日期', trigger: 'change' }]
}

const getStatusType = (status) => {
  const types = { draft: 'info', confirmed: 'warning', received: 'success', cancelled: 'danger' }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = { draft: '草稿', confirmed: '已确认', received: '已入库', cancelled: '已取消' }
  return texts[status] || status
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getPurchases({ page: pagination.page, page_size: pagination.pageSize })
    tableData.value = res.data.items || []
    pagination.total = res.data.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const loadOptions = async () => {
  try {
    const [sRes, pRes] = await Promise.all([getSuppliers({ page: 1, page_size: 100 }), getProducts({ page: 1, page_size: 100 })])
    suppliers.value = sRes.data.items || []
    products.value = pRes.data.items || []
  } catch (e) {
    console.error(e)
  }
}

const handleAdd = () => {
  Object.assign(form, { id: null, supplier_id: null, order_date: new Date().toISOString().split('T')[0], remark: '', items: [] })
  dialogTitle.value = '新建采购订单'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  Object.assign(form, { ...row, items: row.items || [] })
  dialogTitle.value = '编辑采购订单'
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定要删除该订单吗？', '提示', { type: 'warning' })
  try {
    await deletePurchase(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    console.error(e)
  }
}

const handleReceive = async (row) => {
  await ElMessageBox.confirm('确认入库？', '提示', { type: 'info' })
  try {
    await receivePurchase(row.id)
    ElMessage.success('入库成功')
    loadData()
  } catch (e) {
    console.error(e)
  }
}

const addItem = () => {
  form.items.push({ product_id: null, quantity: 1, unit_price: 0, amount: 0 })
}

const onProductChange = (index) => {
  const product = products.value.find(p => p.id === form.items[index].product_id)
  if (product) {
    form.items[index].unit_price = product.cost_price || 0
    calcAmount(form.items[index])
  }
}

const calcAmount = (row) => {
  row.amount = (row.quantity || 0) * (row.unit_price || 0)
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  try {
    if (form.id) {
      await updatePurchase(form.id, form)
      ElMessage.success('更新成功')
    } else {
      await createPurchase(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  loadData()
  loadOptions()
})
</script>

<style scoped>
.purchases .header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.purchases h2 {
  margin: 0;
}
</style>
