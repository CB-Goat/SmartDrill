<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px">
      <h2 style="margin: 0">单元管理</h2>
      <button class="btn-primary" @click="openAdd">添加单元</button>
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
    <table class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>版本</th>
          <th>年级</th>
          <th>科目</th>
          <th>学期</th>
          <th>单元名称</th>
          <th>知识点数</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.id }}</td>
          <td>{{ getVersionName(item.semester_id) }}</td>
          <td>{{ getGradeName(item.semester_id) }}</td>
          <td>{{ getSubjectName(item.semester_id) }}</td>
          <td>{{ getSemesterName(item.semester_id) }}</td>
          <td>{{ item.name }}</td>
          <td>{{ item.knowledge_points?.length || 0 }}</td>
          <td>
            <button class="btn-link" @click="editItem(item)">编辑</button>
            <button class="btn-link" style="color: #f56c6c; margin-left: 8px" @click="deleteItem(item)">删除</button>
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
              <option v-for="sem in filteredSemesters" :key="sem.id" :value="sem.id">{{ sem.name }}</option>
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
import { ref, reactive, computed, onMounted } from 'vue'
import { api } from '@/api'

const items = ref<any[]>([])
const versions = ref<any[]>([])
const grades = ref<any[]>([])
const subjects = ref<any[]>([])
const semesters = ref<any[]>([])
const showForm = ref(false)
const filterVersionId = ref(1)
const filterGradeId = ref(1)
const filterSubjectId = ref(1)
const filterSemesterId = ref(1)
const form = reactive({ id: 0, semester_id: 1, name: '' })

const filteredGrades = computed(() => {
  return grades.value.filter(g => g.version_id === filterVersionId.value)
})

const filteredSubjects = computed(() => {
  return subjects.value.filter(s => s.grade_id === filterGradeId.value)
})

const filteredSemesters = computed(() => {
  return semesters.value.filter(sem => sem.subject_id === filterSubjectId.value)
})

async function onLoad() {
  versions.value = await api.admin.getVersions()
  grades.value = await api.admin.getGrades()
  subjects.value = await api.admin.getSubjects()
  semesters.value = await api.admin.getSemesters()
  
  if (filteredGrades.value.length > 0 && !filteredGrades.value.find(g => g.id === filterGradeId.value)) {
    filterGradeId.value = filteredGrades.value[0].id
  }
  if (filteredSubjects.value.length > 0 && !filteredSubjects.value.find(s => s.id === filterSubjectId.value)) {
    filterSubjectId.value = filteredSubjects.value[0].id
  }
  if (filteredSemesters.value.length > 0 && !filteredSemesters.value.find(sem => sem.id === filterSemesterId.value)) {
    filterSemesterId.value = filteredSemesters.value[0].id
  }
  
  items.value = await api.admin.getUnits(filterSemesterId.value)
}

function onVersionChange() {
  if (filteredGrades.value.length > 0) {
    filterGradeId.value = filteredGrades.value[0].id
  }
  onGradeChange()
}

function onGradeChange() {
  if (filteredSubjects.value.length > 0) {
    filterSubjectId.value = filteredSubjects.value[0].id
  }
  onSubjectChange()
}

function onSubjectChange() {
  if (filteredSemesters.value.length > 0) {
    filterSemesterId.value = filteredSemesters.value[0].id
  }
  onLoad()
}

function getVersionName(semesterId: number) {
  const sem = semesters.value.find(x => x.id === semesterId)
  if (sem) {
    const s = subjects.value.find(x => x.id === sem.subject_id)
    if (s) {
      const g = grades.value.find(x => x.id === s.grade_id)
      if (g) {
        const v = versions.value.find(x => x.id === g.version_id)
        return v?.name || ''
      }
    }
  }
  return ''
}

function getGradeName(semesterId: number) {
  const sem = semesters.value.find(x => x.id === semesterId)
  if (sem) {
    const s = subjects.value.find(x => x.id === sem.subject_id)
    if (s) {
      const g = grades.value.find(x => x.id === s.grade_id)
      return g?.name || ''
    }
  }
  return ''
}

function getSubjectName(semesterId: number) {
  const sem = semesters.value.find(x => x.id === semesterId)
  if (sem) {
    const s = subjects.value.find(x => x.id === sem.subject_id)
    return s?.name || ''
  }
  return ''
}

function getSemesterName(semesterId: number) {
  const sem = semesters.value.find(x => x.id === semesterId)
  return sem?.name || ''
}

function openAdd() {
  Object.assign(form, { id: 0, semester_id: filterSemesterId.value, name: '' })
  showForm.value = true
}

function editItem(item: any) {
  Object.assign(form, item)
  showForm.value = true
}

async function onSubmit() {
  await api.admin.saveUnit(form)
  showForm.value = false
  onLoad()
}

async function deleteItem(item: any) {
  if (!confirm(`确定删除单元"${item.name}"吗？`)) return
  await api.admin.deleteUnit(item.id)
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
  flex-wrap: wrap;
}
.filter-bar select {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  min-width: 150px;
}
</style>