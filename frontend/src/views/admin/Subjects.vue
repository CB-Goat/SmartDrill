<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px">
      <h2 style="margin: 0">科目管理</h2>
      <button class="btn-primary" @click="showForm = true">添加科目</button>
    </div>
    <div class="filter-bar">
      <select v-model="filterGradeId" @change="onLoad">
        <option :value="null">全部年级</option>
        <option v-for="g in grades" :key="g.id" :value="g.id">{{ g.name }}</option>
      </select>
    </div>
    <table class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>年级</th>
          <th>科目名称</th>
          <th>学期数</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.id }}</td>
          <td>{{ getGradeName(item.grade_id) }}</td>
          <td>{{ item.name }}</td>
          <td>{{ item.semesters?.length || 0 }}</td>
          <td>
            <button class="btn-link" @click="editItem(item)">编辑</button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="showForm" class="modal-overlay" @click="showForm = false">
      <div class="modal-content" @click.stop>
        <h3>{{ form.id ? '编辑科目' : '添加科目' }}</h3>
        <form @submit.prevent="onSubmit">
          <div class="form-item">
            <label>年级</label>
            <select v-model="form.grade_id" required>
              <option v-for="g in grades" :key="g.id" :value="g.id">{{ g.name }}</option>
            </select>
          </div>
          <div class="form-item">
            <label>科目名称</label>
            <input v-model="form.name" required placeholder="如：语文、数学、英语" />
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
const grades = ref<any[]>([])
const showForm = ref(false)
const filterGradeId = ref<number | null>(null)
const form = reactive({ id: 0, grade_id: 1, name: '' })

async function onLoad() {
  grades.value = await api.admin.getGrades()
  items.value = await api.admin.getSubjects(filterGradeId.value || undefined)
}

function getGradeName(gradeId: number) {
  const g = grades.value.find(x => x.id === gradeId)
  return g?.name || ''
}

function editItem(item: any) {
  Object.assign(form, item)
  showForm.value = true
}

async function onSubmit() {
  await api.admin.saveSubject(form)
  showForm.value = false
  Object.assign(form, { id: 0, grade_id: 1, name: '' })
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