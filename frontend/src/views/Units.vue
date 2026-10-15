<template>
  <div class="units">
    <div class="header">
      <h2>计量单位管理</h2>
      <el-button type="primary" @click="handleAdd">新增单位</el-button>
    </div>
    <el-card>
      <div class="search-bar">
        <el-input
          v-model="searchText"
          placeholder="搜索单位名称"
          clearable
          style="width: 300px"
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button :icon="Search" @click="handleSearch" />
          </template>
        </el-input>
      </div>
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="单位名称" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="单位名称" prop="name">
          <el-input v-model="form.name" placeholder="例如：个、件、箱、台等" />
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
import { Search } from '@element-plus/icons-vue'
import { getUnits, createUnit, updateUnit, deleteUnit } from '../api/modules/units'

const loading = ref(false)
const tableData = ref([])
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })
const searchText = ref('')

const dialogVisible = ref(false)
const dialogTitle = ref('')
const formRef = ref()
const form = reactive({
  id: null,
  name: ''
})

const rules = {
  name: [{ required: true, message: '请输入单位名称', trigger: 'blur' }]
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getUnits({
      page: pagination.page,
      per_page: pagination.pageSize,
      search: searchText.value
    })
    tableData.value = res.data.items || []
    pagination.total = res.data.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const handleAdd = () => {
  Object.assign(form, { id: null, name: '' })
  dialogTitle.value = '新增单位'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  Object.assign(form, row)
  dialogTitle.value = '编辑单位'
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该单位吗？如果该单位已被商品使用，将无法删除。', '提示', { type: 'warning' })
  } catch {
    return
  }
  
  try {
    await deleteUnit(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    const errorMsg = e.response?.data?.error || '删除失败'
    ElMessage.error(errorMsg)
    console.error(e)
  }
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  try {
    if (form.id) {
      await updateUnit(form.id, form)
      ElMessage.success('更新成功')
    } else {
      await createUnit(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e) {
    const errorMsg = e.response?.data?.error || '操作失败'
    ElMessage.error(errorMsg)
    console.error(e)
  }
}

onMounted(loadData)
</script>

<style scoped>
.units .header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.units h2 {
  margin: 0;
}
.search-bar {
  margin-bottom: 20px;
}
</style>
