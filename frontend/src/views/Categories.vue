<template>
  <div class="categories">
    <div class="header">
      <h2>商品分类管理</h2>
      <el-button type="primary" @click="handleAdd">新增分类</el-button>
    </div>
    <el-card>
      <el-table :data="tableData" v-loading="loading" stripe row-key="id" default-expand-all>
        <el-table-column prop="name" label="分类名称" />
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
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @change="loadData"
        style="margin-top: 20px"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="父分类" prop="parent_id">
          <el-tree-select
            v-model="form.parent_id"
            :data="form.id ? getAvailableParents(form.id) : categoryTree"
            :props="{ label: 'name', value: 'id', children: 'children' }"
            placeholder="请选择父分类（可选）"
            clearable
            check-strictly
          />
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
import { getCategories, getAllCategories, createCategory, updateCategory, deleteCategory } from '../api/modules/categories'

const loading = ref(false)
const tableData = ref([])
const pagination = reactive({ page: 1, pageSize: 100, total: 0 })
const categoryTree = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('')
const formRef = ref()
const form = reactive({
  id: null,
  name: '',
  parent_id: null
})

const rules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }]
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getCategories({ page: pagination.page, per_page: pagination.pageSize })
    tableData.value = res.data.items || []
    pagination.total = res.data.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const loadAllCategories = async () => {
  try {
    const res = await getAllCategories()
    categoryTree.value = res.data || []
  } catch (e) {
    console.error(e)
  }
}

const handleAdd = () => {
  Object.assign(form, { id: null, name: '', parent_id: null })
  dialogTitle.value = '新增分类'
  dialogVisible.value = true
  loadAllCategories()
}

const getAvailableParents = (currentId) => {
  const excludeIds = new Set([currentId])
  
  const addDescendants = (categories) => {
    for (const cat of categories) {
      if (excludeIds.has(cat.id)) {
        if (cat.children) {
          cat.children.forEach(child => {
            excludeIds.add(child.id)
            if (child.children) addDescendants([child])
          })
        }
      }
    }
  }
  
  if (currentId) {
    addDescendants(categoryTree.value)
  }
  
  const filterTree = (categories) => {
    return categories.filter(cat => !excludeIds.has(cat.id)).map(cat => ({
      ...cat,
      children: cat.children ? filterTree(cat.children) : []
    }))
  }
  
  return filterTree(categoryTree.value)
}

const handleEdit = (row) => {
  Object.assign(form, { id: row.id, name: row.name, parent_id: row.parent_id })
  dialogTitle.value = '编辑分类'
  dialogVisible.value = true
  loadAllCategories()
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该分类吗？如果该分类有子分类或商品，将无法删除。', '提示', { type: 'warning' })
  } catch {
    return
  }
  
  try {
    await deleteCategory(row.id)
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
      await updateCategory(form.id, form)
      ElMessage.success('更新成功')
    } else {
      await createCategory(form)
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
.categories .header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.categories h2 {
  margin: 0;
}
</style>
