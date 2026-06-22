<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px">
      <h2 style="margin: 0">知识考点管理</h2>
      <div>
        <button class="btn-primary" @click="importKnowledge" style="margin-right: 8px">知识点导入</button>
        <button class="btn-default" @click="clearKnowledge" style="margin-right: 8px; color: #fa8c16">知识点清除</button>
        <button class="btn-primary" @click="importExamPoints" style="margin-right: 8px">考点导入</button>
        <button class="btn-default" @click="clearExamPoints" style="margin-right: 8px; color: #f5222d">考点清除</button>
      </div>
    </div>
    
    <div class="filter-bar">
      <select v-model="filterVersionId" @change="onVersionChange">
        <option v-for="v in versions" :key="v.id" :value="v.id">{{ v.name }}</option>
      </select>
      <select v-model="filterGradeId" @change="onGradeChange">
        <option v-for="g in filteredGrades" :key="g.id" :value="g.id">{{ g.name }}</option>
      </select>
      <select v-model="filterSubjectId" @change="onSubjectChange">
        <option v-for="s in filteredSubjects" :key="s.id" :value="s.id">{{ s.name }}</option>
      </select>
      <select v-model="filterSemesterId" @change="onLoad">
        <option v-for="sem in filteredSemesters" :key="sem.id" :value="sem.id">{{ sem.name }}</option>
      </select>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { api } from '@/api'

const items = ref<any[]>([])
const versions = ref<any[]>([])
const grades = ref<any[]>([])
const subjects = ref<any[]>([])
const semesters = ref<any[]>([])
const importFile = ref<File | null>(null)

const filterVersionId = ref(1)
const filterGradeId = ref<number | null>(null)
const filterSubjectId = ref<number | null>(null)
const filterSemesterId = ref<number | null>(null)

const filteredGrades = computed(() => grades.value.filter(g => g.version_id === filterVersionId.value))
const filteredSubjects = computed(() => filterGradeId.value ? subjects.value.filter(s => s.grade_id === filterGradeId.value) : subjects.value.filter(s => {
  const grade = grades.value.find(g => g.id === s.grade_id)
  return grade && grade.version_id === filterVersionId.value
}))
const filteredSemesters = computed(() => filterSubjectId.value ? semesters.value.filter(sem => sem.subject_id === filterSubjectId.value) : semesters.value.filter(sem => {
  const subject = subjects.value.find(s => s.id === sem.subject_id)
  if (!subject) return false
  if (filterGradeId.value) return subject.grade_id === filterGradeId.value
  const grade = grades.value.find(g => g.id === subject.grade_id)
  return grade && grade.version_id === filterVersionId.value
}))

async function onLoad() {
  versions.value = await api.admin.getVersions()
  grades.value = await api.admin.getGrades()
  subjects.value = await api.admin.getSubjects()
  semesters.value = await api.admin.getSemesters()
  
  if (filteredGrades.value.length > 0 && !filterGradeId.value) {
    filterGradeId.value = filteredGrades.value[0].id
  }
}

function onVersionChange() {
  filterGradeId.value = null
  filterSubjectId.value = null
  filterSemesterId.value = null
  onLoad()
}

function onGradeChange() {
  filterSubjectId.value = null
  filterSemesterId.value = null
}

function getFilterScope() {
  return {
    version_id: filterVersionId.value,
    grade_id: filterGradeId.value,
    subject_id: filterSubjectId.value,
    semester_id: filterSemesterId.value
  }
}

async function importKnowledge() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.xlsx,.xls'
  input.onchange = async (e: any) => {
    const file = e.target.files[0]
    if (!file) return
    
    const formData = new FormData()
    formData.append('file', file)
    formData.append('version_id', String(filterVersionId.value))
    if (filterGradeId.value) formData.append('grade_id', String(filterGradeId.value))
    if (filterSubjectId.value) formData.append('subject_id', String(filterSubjectId.value))
    if (filterSemesterId.value) formData.append('semester_id', String(filterSemesterId.value))
    
    try {
      const response = await fetch('/api/admin/import-knowledge', {
        method: 'POST',
        headers: { 'Authorization': 'Bearer ' + localStorage.getItem('admin_token') },
        body: formData
      })
      const result = await response.json()
      alert(result.message + '\n' + (result.log?.join('\n') || ''))
    } catch (error) {
      alert('导入失败')
    }
  }
  input.click()
}

async function clearKnowledge() {
  const scope = getFilterScope()
  let msg = '确定清除知识点吗？\n范围：'
  if (scope.semester_id) msg += '当前学期'
  else if (scope.subject_id) msg += '当前科目所有学期'
  else if (scope.grade_id) msg += '当前年级所有科目'
  else msg += '当前版本所有年级'
  
  if (!confirm(msg)) return
  
  try {
    const response = await fetch('/api/admin/clear-knowledge', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + localStorage.getItem('admin_token'),
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(scope)
    })
    const result = await response.json()
    alert(result.message)
  } catch (error) {
    alert('清除失败')
  }
}

async function importExamPoints() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.xlsx,.xls'
  input.onchange = async (e: any) => {
    const file = e.target.files[0]
    if (!file) return
    
    const formData = new FormData()
    formData.append('file', file)
    formData.append('version_id', String(filterVersionId.value))
    if (filterGradeId.value) formData.append('grade_id', String(filterGradeId.value))
    if (filterSubjectId.value) formData.append('subject_id', String(filterSubjectId.value))
    if (filterSemesterId.value) formData.append('semester_id', String(filterSemesterId.value))
    
    try {
      const response = await fetch('/api/admin/import-exam-points', {
        method: 'POST',
        headers: { 'Authorization': 'Bearer ' + localStorage.getItem('admin_token') },
        body: formData
      })
      const result = await response.json()
      alert(result.message + '\n' + (result.log?.join('\n') || ''))
    } catch (error) {
      alert('导入失败')
    }
  }
  input.click()
}

async function clearExamPoints() {
  const scope = getFilterScope()
  let msg = '确定清除考点吗？\n范围：'
  if (scope.semester_id) msg += '当前学期'
  else if (scope.subject_id) msg += '当前科目所有学期'
  else if (scope.grade_id) msg += '当前年级所有科目'
  else msg += '当前版本所有年级'
  
  if (!confirm(msg)) return
  
  try {
    const response = await fetch('/api/admin/clear-exam-points', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + localStorage.getItem('admin_token'),
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(scope)
    })
    const result = await response.json()
    alert(result.message)
  } catch (error) {
    alert('清除失败')
  }
}

onMounted(onLoad)
</script>

<style scoped src="./table.css"></style>
<style scoped>
.filter-bar {
  margin-bottom: 16px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.filter-bar select {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  min-width: 150px;
}

.import-tips {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  margin: 16px 0;
}

.import-tips p {
  margin: 4px 0;
  color: #666;
  font-size: 12px;
}
</style>
