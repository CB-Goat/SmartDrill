<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px">
      <h2 style="margin: 0">单元管理</h2>
      <button class="btn-primary" @click="showForm = true">添加单元</button>
    </div>
    <div class="filter-bar">
      <select v-model="filterSemesterId" @change="onLoad">
        <option :value="null">全部学期</option>
        <option v-for="s in semesters" :key="s.id" :value="s.id">{{ s.name }}</option>
      </select>
    </div>
    <table class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>学期</th>
          <th>单元名称</th>
          <th>知识点数</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.id }}</td>
          <td>{{ getSemesterName(item.semester_id) }}</td>
          <td>{{ item.name }}</td>
          <td>{{ item.knowledge_points?.length || 0 }}</td>
          <td>
            <button class="btn-link" @click="editItem(item)">编辑</button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="showForm" class="modal-overlay" @click="showForm = false">
      <div class="modal-content" @click.stop>
        <h3>{{ form.id ? '编辑单元' : '添加单元' }}</h3>
        <form @submit.prevent="onSubmit">
          <div class="form-item">
            <label>学期</label>
            <select v-model="form.semester_id" required>
              <option v-for="s in semesters" :key="s.id" :value="s.id">{{ s.name }}</option>
            </select>
          </div>
          <div class="form-item">
            <label>单元名称</label>
            <input v-model="form.name" required placeholder="如：第一单元、第二单元" />
          </div>
          <div class="form-actions">
            <button type="button" class="btn-default" @click="showForm = false">取消</button>
            <button type="submit" class="btn-primary">保存</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { api } from '@/api'

const items = ref<any[]>([])
const semesters = ref<any[]>([])
const showForm = ref(false)
const filterSemesterId = ref<number | null>(null)
const form = reactive({ id: 0, semester_id: 1, name: '' })

async function onLoad() {
  semesters.value = await api.admin.getSemesters()
  items.value = await api.admin.getUnits(filterSemesterId.value || undefined)
}

function getSemesterName(semesterId: number) {
  const s = semesters.value.find(x => x.id === semesterId)
  return s?.name || ''
}

function editItem(item: any) {
  Object.assign(form, item)
  showForm.value = true
}

async function onSubmit() {
  await api.admin.saveUnit(form)
  showForm.value = false
  Object.assign(form, { id: 0, semester_id: 1, name: '' })
  onLoad()
}

onMounted(onLoad)
</script>

<style scoped src="./table.css"></style>
<style scoped>
.filter-bar {
  margin-bottom: 16px;
}
.filter-bar select {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  min-width: 200px;
}
</style>