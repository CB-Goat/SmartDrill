<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px">
      <h2 style="margin: 0">知识考点管理</h2>
      <div>
        <button class="btn-primary" @click="importKnowledge" style="margin-right: 8px">知识点导入</button>
        <button class="btn-default" @click="clearKnowledge" style="margin-right: 8px; color: #fa8c16">知识点清除</button>
        <button class="btn-primary" @click="importExamPoints" style="margin-right: 8px">考点导入</button>
        <button class="btn-default" @click="clearExamPoints" style="margin-right: 8px; color: #f5222d">考点清除</button>
        <button class="btn-default" @click="fixExamContent" style="margin-right: 8px; color: #52c41a">修复考点</button>
      </div>
    </div>
    
    <div class="filter-bar">
      <select v-model="filterVersionId" @change="onVersionChange">
        <option v-for="v in versions" :key="v.id" :value="v.id">{{ v.name }}</option>
      </select>
      <select v-model="filterGradeId" @change="onGradeChange">
        <option :value="null">全部年级</option>
        <option v-for="g in filteredGrades" :key="g.id" :value="g.id">{{ g.name }}</option>
      </select>
      <select v-model="filterSubjectId" @change="onSubjectChange">
        <option :value="null">全部科目</option>
        <option v-for="s in filteredSubjects" :key="s.id" :value="s.id">{{ s.name }}</option>
      </select>
      <select v-model="filterSemesterId">
        <option :value="null">全部学期</option>
        <option v-for="sem in filteredSemesters" :key="sem.id" :value="sem.id">{{ sem.name }}</option>
      </select>
      <button class="btn-primary" @click="queryData">查询</button>
    </div>
    
    <div v-if="queryResults.length > 0" class="query-results">
      <h3>查询结果（{{ queryResults.length }}个单元）</h3>
      <table class="data-table">
        <thead>
          <tr>
            <th>单元ID</th>
            <th>年级</th>
            <th>科目</th>
            <th>学期</th>
            <th>单元序号</th>
            <th>单元名称</th>
            <th>知识点</th>
            <th>考点数</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="unit in queryResults" :key="unit.id">
            <td>{{ unit.id }}</td>
            <td>{{ unit.grade_name }}</td>
            <td>{{ unit.subject_name }}</td>
            <td>{{ unit.semester_name }}</td>
            <td>{{ unit.unit_number }}</td>
            <td>{{ unit.name }}</td>
            <td>{{ unit.has_knowledge ? '✓' : '✗' }}</td>
            <td>{{ unit.exam_point_count }}</td>
            <td>
              <button class="btn-link" @click="previewUnit(unit)">预览</button>
              <button class="btn-link" @click="downloadWord(unit)" style="margin-left: 8px">下载</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <div v-if="previewVisible" class="modal-overlay" @click="previewVisible = false">
      <div class="modal-content word-preview" @click.stop>
        <div class="modal-header">
          <h3>{{ previewData?.unit_name }}</h3>
          <div>
            <button class="btn-primary" @click="downloadCurrentWord" style="margin-right: 8px">下载Word</button>
            <button class="close-btn" @click="previewVisible = false">×</button>
          </div>
        </div>
        <div class="modal-body word-container">
          <div class="word-page">
            <div class="page-title">{{ previewData?.unit_name }}</div>
            <div class="section-title">知识点</div>
            <div class="content-area">
              <div v-if="previewData?.knowledge?.content" class="knowledge-content">
                <p v-for="(line, idx) in previewData.knowledge.content.split('\n')" :key="idx">{{ line }}</p>
              </div>
              <div v-else class="empty-hint">暂无知识点内容</div>
            </div>
          </div>
          <div class="word-page">
            <div class="section-title">考点</div>
            <div class="content-area">
              <div v-if="previewData?.exam_points?.length > 0" class="exam-points-list">
                <div v-for="(ep, idx) in previewData.exam_points" :key="ep.id" class="exam-item">
                  <div class="exam-title-row">
                    <span class="exam-num">{{ idx + 1 }}.</span>
                    <span class="exam-title">{{ ep.title }}</span>
                    <span v-if="ep.exam_frequency" class="freq-badge" :class="'freq-' + ep.exam_frequency">{{ ep.exam_frequency }}</span>
                  </div>
                  <div v-if="ep.exam_types" class="exam-types">题型：{{ ep.exam_types }}</div>
                  <div v-if="ep.content" class="exam-content">
                    <p v-for="(line, lineIdx) in ep.content.split('\n')" :key="lineIdx">{{ line }}</p>
                  </div>
                </div>
              </div>
              <div v-else class="empty-hint">暂无考点内容</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { api } from '@/api'

const versions = ref<any[]>([])
const grades = ref<any[]>([])
const subjects = ref<any[]>([])
const semesters = ref<any[]>([])
const queryResults = ref<any[]>([])

const filterVersionId = ref(1)
const filterGradeId = ref<number | null>(null)
const filterSubjectId = ref<number | null>(null)
const filterSemesterId = ref<number | null>(null)

const previewVisible = ref(false)
const previewData = ref<any>(null)

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
}

function onVersionChange() {
  filterGradeId.value = null
  filterSubjectId.value = null
  filterSemesterId.value = null
}

function onGradeChange() {
  filterSubjectId.value = null
  filterSemesterId.value = null
}

function onSubjectChange() {
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

async function queryData() {
  const scope = getFilterScope()
  try {
    const response = await fetch('/api/admin/query-units', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + localStorage.getItem('admin_token'),
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(scope)
    })
    const result = await response.json()
    queryResults.value = result.units || []
  } catch (error) {
    alert('查询失败')
  }
}

async function previewUnit(unit: any) {
  try {
    const response = await fetch(`/api/admin/unit-detail/${unit.id}`, {
      headers: { 'Authorization': 'Bearer ' + localStorage.getItem('admin_token') }
    })
    const result = await response.json()
    previewData.value = {
      unit_id: unit.id,
      unit_name: `${unit.grade_name} ${unit.subject_name} ${unit.semester_name} - ${unit.name}`,
      knowledge: result.knowledge,
      exam_points: result.exam_points
    }
    previewVisible.value = true
  } catch (error) {
    alert('获取详情失败')
  }
}

async function downloadWord(unit: any) {
  const token = localStorage.getItem('admin_token')
  const url = `/api/admin/unit-word/${unit.id}`
  const response = await fetch(url, {
    headers: { 'Authorization': 'Bearer ' + token }
  })
  const blob = await response.blob()
  const downloadUrl = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = downloadUrl
  a.download = `${unit.grade_name} ${unit.subject_name} ${unit.semester_name} - ${unit.name}.docx`
  a.click()
  window.URL.revokeObjectURL(downloadUrl)
}

async function downloadCurrentWord() {
  if (!previewData.value) return
  const unit = queryResults.value.find(u => u.id === previewData.value.unit_id)
  if (unit) {
    await downloadWord(unit)
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

async function fixExamContent() {
  if (!confirm('确定修复考点内容吗？\n将根据冒号分隔标题和内容')) return
  
  try {
    const response = await fetch('/api/admin/clean-exam-content', {
      method: 'POST',
      headers: { 'Authorization': 'Bearer ' + localStorage.getItem('admin_token') }
    })
    const result = await response.json()
    alert(result.message)
  } catch (error) {
    alert('修复失败')
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
  align-items: center;
}
.filter-bar select {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  min-width: 150px;
}

.query-results {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-top: 20px;
}

.query-results h3 {
  margin: 0 0 16px 0;
  color: #333;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.data-table th {
  background: #fafafa;
  font-weight: 500;
  color: #333;
}

.data-table tbody tr:hover {
  background: #f5f5f5;
}

.btn-link {
  background: none;
  border: none;
  color: #1890ff;
  cursor: pointer;
  padding: 4px 8px;
  font-size: 14px;
}

.btn-link:hover {
  color: #40a9ff;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #fff;
  border-radius: 8px;
  width: 90%;
  max-width: 900px;
  max-height: 85vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 16px 24px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.section {
  margin-bottom: 24px;
}

.section h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #333;
  border-left: 3px solid #1890ff;
  padding-left: 12px;
}

.content-box {
  background: #f5f5f5;
  border-radius: 4px;
  padding: 16px;
}

.content-box pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.6;
}

.empty-text {
  color: #999;
  font-size: 14px;
}

.exam-point-item {
  background: #f5f5f5;
  border-radius: 4px;
  padding: 16px;
  margin-bottom: 12px;
}

.ep-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.ep-title {
  font-weight: 500;
  color: #333;
  flex: 1;
}

.ep-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #fff;
}

.freq-必考 {
  background: #f5222d;
}

.freq-常考 {
  background: #fa8c16;
}

.freq-少考 {
  background: #52c41a;
}

.ep-types {
  color: #666;
  font-size: 12px;
}

.ep-content {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.6;
  color: #333;
}

.word-preview {
  max-width: 1000px;
}

.word-container {
  background: #f0f0f0;
  padding: 20px;
  display: flex;
  gap: 20px;
  overflow-x: auto;
}

.word-page {
  background: #fff;
  width: 595px;
  min-height: 842px;
  padding: 72px 90px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  flex-shrink: 0;
}

.page-title {
  font-size: 18px;
  font-weight: bold;
  text-align: center;
  margin-bottom: 30px;
  color: #000;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  color: #0066cc;
  margin-bottom: 20px;
  padding-bottom: 8px;
  border-bottom: 2px solid #0066cc;
}

.content-area {
  font-size: 12pt;
  line-height: 1.8;
  color: #000;
}

.knowledge-content p,
.exam-content p {
  margin: 0 0 8px 0;
  text-indent: 2em;
}

.empty-hint {
  color: #999;
  font-style: italic;
}

.exam-points-list {
  margin-top: 10px;
}

.exam-item {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px dashed #e0e0e0;
}

.exam-item:last-child {
  border-bottom: none;
}

.exam-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.exam-num {
  font-weight: bold;
  color: #000;
}

.exam-title {
  font-size: 14px;
  font-weight: bold;
  color: #000;
  flex: 1;
}

.freq-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #fff;
  font-weight: normal;
}

.exam-types {
  font-size: 11pt;
  color: #666;
  margin-bottom: 8px;
}

.exam-content {
  margin-top: 8px;
}
</style>
