<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px">
      <h2 style="margin: 0">科目管理</h2>
      <button class="btn-primary" @click="openAdd">添加科目</button>
    </div>
    <div class="filter-bar">
      <select v-model="filterVersionId" @change="onVersionChange">
        <option v-for="v in versions" :key="v.id" :value="v.id">{{ v.name }}</option>
      </select>
      <select v-model="filterGradeId" @change="onLoad">
        <option v-for="g in filteredGrades" :key="g.id" :value="g.id">{{ g.name }}</option>
      </select>
    </div>
    <table class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>版本</th>
          <th>年级</th>
          <th>科目名称</th>
          <th>学期数</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.id }}</td>
          <td>{{ getVersionName(item.grade_id) }}</td>
          <td>{{ getGradeName(item.grade_id) }}</td>
          <td>{{ item.name }}</td>
          <td>{{ item.semesters?.length || 0 }}</td>
          <td>
            <button class="btn-link" @click="editItem(item)">编辑</button>
            <button class="btn-link" style="color: #f56c6c; margin-left: 8px" @click="deleteItem(item)">删除</button>
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
              <option v-for="g in filteredGrades" :key="g.id" :value="g.id">{{ g.name }}</option>
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
import { ref, reactive, computed, onMounted } from 'vue'
import { api } from '@/api'

const items = ref<any[]>([])
const versions = ref<any[]>([])
const grades = ref<any[]>([])
const showForm = ref(false)
const filterVersionId = ref(1)
const filterGradeId = ref(1)
const form = reactive({ id: 0, grade_id: 1, name: '' })

const filteredGrades = computed(() => {
  return grades.value.filter(g => g.version_id === filterVersionId.value)
})

async function onLoad() {
  versions.value = await api.admin.getVersions()
  grades.value = await api.admin.getGrades()
  if (filteredGrades.value.length > 0 && !filteredGrades.value.find(g => g.id === filterGradeId.value)) {
    filterGradeId.value = filteredGrades.value[0].id
  }
  items.value = await api.admin.getSubjects(filterGradeId.value)
}

function onVersionChange() {
  if (filteredGrades.value.length > 0) {
    filterGradeId.value = filteredGrades.value[0].id
  }
  onLoad()
}

function getVersionName(gradeId: number) {
  const g = grades.value.find(x => x.id === gradeId)
  if (g) {
    const v = versions.value.find(x => x.id === g.version_id)
    return v?.name || ''
  }
  return ''
}

function getGradeName(gradeId: number) {
  const g = grades.value.find(x => x.id === gradeId)
  return g?.name || ''
}

function openAdd() {
  Object.assign(form, { id: 0, grade_id: filterGradeId.value, name: '' })
  showForm.value = true
}

function editItem(item: any) {
  Object.assign(form, item)
  showForm.value = true
}

async function onSubmit() {
  await api.admin.saveSubject(form)
  showForm.value = false
  onLoad()
}

async function deleteItem(item: any) {
  if (!confirm(`确定删除科目"${item.name}"吗？`)) return
  await api.admin.deleteSubject(item.id)
  onLoad()
}

onMounted(onLoad)
</script>

<style scoped src="./table.css"></style>
<style scoped>
.filter-bar {
  margin-bottom: 16px;
  display: flex;
  gap: 8px;
}
.filter-bar select {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  min-width: 200px;
}
</style>