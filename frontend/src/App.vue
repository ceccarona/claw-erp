<template>
  <div class="app">
    <header>
      <h1>🏭 Claw ERP 进销存管理系统</h1>
    </header>
    <main>
      <div class="status">
        <p>后端连接状态: {{ status }}</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const status = ref('连接中...')

onMounted(async () => {
  try {
    const res = await axios.get('/api/health')
    status.value = res.data.message || '已连接'
  } catch (e) {
    status.value = '未连接'
  }
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
.app {
  font-family: Arial, sans-serif;
  padding: 20px;
}
header {
  background: #1890ff;
  color: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}
.status {
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
}
</style>
