<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px">
      <h2 style="margin: 0">题库管理</h2>
      <div style="display: flex; gap: 12px">
        <button class="btn-default" @click="triggerImport">
          <input ref="fileInput" type="file" accept=".xlsx,.xls" @change="handleImport" style="display: none" />
          导入题库
        </button>
        <button class="btn-danger" @click="confirmClear">清除题库</button>
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
      <select v-model="filterSemesterId" @change="onSemesterChange">
        <option :value="null">全部学期</option>
        <option v-for="sem in filteredSemesters" :key="sem.id" :value="sem.id">{{ sem.name }}</option>
      </select>
      <select v-model="filterUnitId">
        <option :value="null">全部单元</option>
        <option v-for="u in filteredUnits" :key="u.id" :value="u.id">{{ u.name }}</option>
      </select>
      <select v-model="filterQuestionTypeId">
        <option :value="null">全部题型</option>
        <option v-for="qt in questionTypes" :key="qt.id" :value="qt.id">{{ qt.name }}</option>
      </select>
      <select v-model="filterDifficultyId">
        <option :value="null">全部难度</option>
        <option v-for="d in difficulties" :key="d.id" :value="d.id">{{ d.name }}</option>
      </select>
      <button class="btn-primary" @click="queryData">查询</button>
    </div>

    <table class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>年级</th>
          <th>科目</th>
          <th>学期</th>
          <th>单元</th>
          <th>题型</th>
          <th>难度</th>
          <th>题目</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="q in questions" :key="q.id">
          <td>{{ q.id }}</td>
          <td>{{ q.grade_name || '-' }}</td>
          <td>{{ q.subject_name || '-' }}</td>
          <td>{{ q.semester_name || '-' }}</td>
          <td>{{ q.unit_name || '-' }}</td>
          <td>{{ q.question_type || '-' }}</td>
          <td>{{ q.difficulty || '-' }}</td>
          <td class="question-content">{{ getQuestionDisplay(q) }}</td>
          <td>
            <button class="btn-link" @click="viewQuestion(q)">查看</button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="total > 0" class="pagination">
      <div class="pagination-info">共 {{ total }} 条，第 {{ currentPage }}/{{ totalPages }} 页</div>
      <div class="pagination-controls">
        <button class="btn-default" :disabled="currentPage <= 1" @click="onPageChange(1)">首页</button>
        <button class="btn-default" :disabled="currentPage <= 1" @click="onPageChange(currentPage - 1)">上一页</button>
        <button class="btn-default" :disabled="currentPage >= totalPages" @click="onPageChange(currentPage + 1)">下一页</button>
        <button class="btn-default" :disabled="currentPage >= totalPages" @click="onPageChange(totalPages)">末页</button>
      </div>
    </div>

    <div v-if="viewVisible" class="modal-overlay" @click="viewVisible = false">
      <div class="modal-content large-modal" @click.stop>
        <div class="modal-header">
          <h3>题目详情</h3>
          <button class="close-btn" @click="viewVisible = false">×</button>
        </div>
        <div class="modal-body">
          <div class="detail-row">
            <span class="detail-label">ID：</span>
            <span>{{ currentQuestion?.id }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">年级：</span>
            <span>{{ currentQuestion?.grade_name || '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">科目：</span>
            <span>{{ currentQuestion?.subject_name || '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">学期：</span>
            <span>{{ currentQuestion?.semester_name || '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">单元：</span>
            <span>{{ currentQuestion?.unit_name || '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">题型：</span>
            <span>{{ currentQuestion?.question_type || '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">难度：</span>
            <span>{{ currentQuestion?.difficulty || '-' }}</span>
          </div>
          <div class="detail-block">
            <span class="detail-label">题目内容：</span>
            <pre class="detail-content">{{ currentQuestion?.content || '-' }}</pre>
          </div>
          <div class="detail-block">
            <span class="detail-label">JSON数据：</span>
            <pre class="detail-content json-content">{{ formatJson(currentQuestion?.question_json) }}</pre>
          </div>
          <div class="detail-block">
            <span class="detail-label">答案：</span>
            <pre class="detail-content">{{ currentQuestion?.answer || '-' }}</pre>
          </div>
          <div class="detail-block">
            <span class="detail-label">解析：</span>
            <pre class="detail-content">{{ currentQuestion?.analysis || '-' }}</pre>
          </div>
        </div>
      </div>
    </div>

    <div v-if="clearConfirmVisible" class="modal-overlay" @click="clearConfirmVisible = false">
      <div class="modal-content" @click.stop>
        <h3>确认清除题库</h3>
        <p style="margin: 16px 0; color: rgba(0,0,0,0.85);">
          确定要清除以下范围的题目吗？<br/>
          此操作不可恢复！
        </p>
        <div class="clear-scope-info">
          <div v-if="filterVersionId">版本：{{ getVersionName(filterVersionId) }}</div>
          <div v-if="filterGradeId">年级：{{ getGradeName(filterGradeId) }}</div>
          <div v-if="filterSubjectId">科目：{{ getSubjectName(filterSubjectId) }}</div>
          <div v-if="filterSemesterId">学期：{{ getSemesterName(filterSemesterId) }}</div>
          <div v-if="filterUnitId">单元：{{ getUnitName(filterUnitId) }}</div>
          <div v-if="!filterGradeId && !filterSubjectId && !filterSemesterId && !filterUnitId" style="color: #ff4d4f;">
            未选择具体范围，将清除该版本下所有题目！
          </div>
        </div>
        <div class="form-actions">
          <button type="button" class="btn-default" @click="clearConfirmVisible = false">取消</button>
          <button type="button" class="btn-danger" @click="clearQuestions" :disabled="clearing">确认清除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { api } from '@/api'
import axios from 'axios'

const questions = ref<any[]>([])
const viewVisible = ref(false)
const currentQuestion = ref<any>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const importing = ref(false)
const clearConfirmVisible = ref(false)
const clearing = ref(false)

const versions = ref<any[]>([])
const grades = ref<any[]>([])
const subjects = ref<any[]>([])
const semesters = ref<any[]>([])
const units = ref<any[]>([])
const questionTypes = ref<any[]>([])
const difficulties = ref<any[]>([])

const filterVersionId = ref(1)
const filterGradeId = ref<number | null>(null)
const filterSubjectId = ref<number | null>(null)
const filterSemesterId = ref<number | null>(null)
const filterUnitId = ref<number | null>(null)
const filterQuestionTypeId = ref<number | null>(null)
const filterDifficultyId = ref<number | null>(null)

const currentPage = ref(1)
const pageSize = ref(50)
const total = ref(0)
const totalPages = ref(0)

const filteredGrades = computed(() => grades.value.filter(g => g.version_id === filterVersionId.value))
const filteredSubjects = computed(() => {
  if (filterGradeId.value) {
    return subjects.value.filter(s => s.grade_id === filterGradeId.value)
  }
  return subjects.value.filter(s => {
    const grade = grades.value.find(g => g.id === s.grade_id)
    return grade && grade.version_id === filterVersionId.value
  })
})
const filteredSemesters = computed(() => {
  if (filterSubjectId.value) {
    return semesters.value.filter(sem => sem.subject_id === filterSubjectId.value)
  }
  return semesters.value.filter(sem => {
    const subject = subjects.value.find(s => s.id === sem.subject_id)
    if (!subject) return false
    if (filterGradeId.value) return subject.grade_id === filterGradeId.value
    const grade = grades.value.find(g => g.id === subject.grade_id)
    return grade && grade.version_id === filterVersionId.value
  })
})
const filteredUnits = computed(() => {
  if (filterSemesterId.value) {
    return units.value.filter(u => u.semester_id === filterSemesterId.value)
  }
  return units.value
})

async function onLoad() {
  const [vers, gras, subs, sems, uns, qts, diffs] = await Promise.all([
    api.admin.getVersions(),
    api.admin.getGrades(),
    api.admin.getSubjects(),
    api.admin.getSemesters(),
    api.admin.getUnits(),
    api.admin.getQuestionTypes(),
    api.admin.getDifficulties()
  ])
  versions.value = vers
  grades.value = gras
  subjects.value = subs
  semesters.value = sems
  units.value = uns
  questionTypes.value = qts
  difficulties.value = diffs

  if (versions.value.length > 0 && !filterVersionId.value) {
    filterVersionId.value = versions.value[0].id
  }

  queryData()
}

function onVersionChange() {
  filterGradeId.value = null
  filterSubjectId.value = null
  filterSemesterId.value = null
  filterUnitId.value = null
}

function onGradeChange() {
  filterSubjectId.value = null
  filterSemesterId.value = null
  filterUnitId.value = null
}

function onSubjectChange() {
  filterSemesterId.value = null
  filterUnitId.value = null
}

function onSemesterChange() {
  filterUnitId.value = null
}

async function queryData() {
  currentPage.value = 1
  await loadQuestions()
}

async function loadQuestions() {
  const params: any = {
    page: currentPage.value,
    page_size: pageSize.value
  }
  if (filterVersionId.value) params.version_id = filterVersionId.value
  if (filterGradeId.value) params.grade_id = filterGradeId.value
  if (filterSubjectId.value) params.subject_id = filterSubjectId.value
  if (filterSemesterId.value) params.semester_id = filterSemesterId.value
  if (filterUnitId.value) params.unit_id = filterUnitId.value
  if (filterQuestionTypeId.value) params.question_type_id = filterQuestionTypeId.value
  if (filterDifficultyId.value) params.difficulty_id = filterDifficultyId.value

  const res: any = await api.admin.getQuestions(params)
  questions.value = res.items || []
  total.value = res.total || 0
  totalPages.value = res.total_pages || 0
}

function onPageChange(page: number) {
  currentPage.value = page
  loadQuestions()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function getQuestionDisplay(q: any) {
  if (q.question_json && q.question_json.stem) {
    const stem = q.question_json.stem
    return stem.length > 50 ? stem.substring(0, 50) + '...' : stem
  }
  if (q.content) {
    return q.content.length > 50 ? q.content.substring(0, 50) + '...' : q.content
  }
  return '-'
}

function viewQuestion(q: any) {
  currentQuestion.value = q
  viewVisible.value = true
}

function formatJson(obj: any) {
  if (!obj) return '-'
  const orderedKeys = ['question_type', 'stem', 'content', 'answer', 'analysis']
  try {
    const parsed = typeof obj === 'string' ? JSON.parse(obj) : obj
    const ordered: any = {}
    for (const key of orderedKeys) {
      if (parsed.hasOwnProperty(key)) {
        ordered[key] = parsed[key]
      }
    }
    for (const key of Object.keys(parsed)) {
      if (!orderedKeys.includes(key)) {
        ordered[key] = parsed[key]
      }
    }
    return JSON.stringify(ordered, null, 2)
  } catch {
    return String(obj)
  }
}

function getVersionName(id: number) {
  return versions.value.find(v => v.id === id)?.name || '-'
}

function getGradeName(id: number | null) {
  if (!id) return '-'
  return grades.value.find(g => g.id === id)?.name || '-'
}

function getSubjectName(id: number | null) {
  if (!id) return '-'
  return subjects.value.find(s => s.id === id)?.name || '-'
}

function getSemesterName(id: number | null) {
  if (!id) return '-'
  return semesters.value.find(s => s.id === id)?.name || '-'
}

function getUnitName(id: number | null) {
  if (!id) return '-'
  return units.value.find(u => u.id === id)?.name || '-'
}

function confirmClear() {
  clearConfirmVisible.value = true
}

async function clearQuestions() {
  clearing.value = true
  try {
    const params: any = {}
    if (filterVersionId.value) params.version_id = filterVersionId.value
    if (filterGradeId.value) params.grade_id = filterGradeId.value
    if (filterSubjectId.value) params.subject_id = filterSubjectId.value
    if (filterSemesterId.value) params.semester_id = filterSemesterId.value
    if (filterUnitId.value) params.unit_id = filterUnitId.value

    const res: any = await api.admin.deleteQuestions(params)
    alert(res.message || `成功删除 ${res.deleted} 道题目`)
    clearConfirmVisible.value = false
    loadQuestions()
  } catch (error: any) {
    alert('清除失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    clearing.value = false
  }
}

function triggerImport() {
  fileInput.value?.click()
}

async function handleImport(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  importing.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)

    const adminToken = localStorage.getItem('admin_token')
    const response = await axios.post('/api/admin/import-questions', formData, {
      headers: {
        'Authorization': `Bearer ${adminToken}`,
        'Content-Type': 'multipart/form-data'
      },
      timeout: 120000
    })

    const result = response.data

    if (result) {
      let msg = `导入完成！\n成功: ${result.imported}\n跳过: ${result.skipped}`
      if (result.skip_reasons) {
        msg += '\n\n跳过原因统计:'
        for (const [reason, count] of Object.entries(result.skip_reasons)) {
          if (count && (count as number) > 0) {
            msg += `\n  ${reason}: ${count}`
          }
        }
      }
      if (result.skip_details && result.skip_details.length > 0) {
        msg += `\n\n部分跳过详情(前${result.skip_details.length}条):\n`
        msg += result.skip_details.slice(0, 10).join('\n')
      }
      alert(msg)
      loadQuestions()
    }
  } catch (error: any) {
    if (error.code === 'ECONNABORTED') {
      alert('导入超时，请尝试分批导入或联系管理员')
    } else {
      alert('导入失败: ' + (error.response?.data?.detail || error.message))
    }
  } finally {
    importing.value = false
    if (target) target.value = ''
  }
}

onMounted(onLoad)
</script>

<style scoped>
.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  padding: 16px;
  background: #fff;
  border-radius: 4px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-bar select {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  min-width: 120px;
  background: #fff;
}

.data-table {
  width: 100%;
  background: #fff;
  border-radius: 4px;
  border-collapse: collapse;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.data-table th,
.data-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
}

.data-table th {
  background: #fafafa;
  color: rgba(0, 0, 0, 0.85);
  font-weight: 500;
  white-space: nowrap;
}

.data-table tbody tr:hover {
  background: #fafafa;
}

.question-content {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-primary {
  background: #1890ff;
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-default {
  background: #fff;
  color: rgba(0, 0, 0, 0.65);
  border: 1px solid #d9d9d9;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-default:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-danger {
  background: #fff;
  color: #ff4d4f;
  border: 1px solid #ff4d4f;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-danger:hover {
  background: #ff4d4f;
  color: #fff;
}

.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-link {
  background: none;
  color: #1890ff;
  border: none;
  cursor: pointer;
  padding: 0;
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
  padding: 24px;
  border-radius: 4px;
  width: 600px;
  max-height: 80vh;
  overflow: auto;
}

.large-modal {
  width: 900px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.modal-header h3 {
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  padding: 0;
  line-height: 1;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 0;
}

.clear-scope-info {
  background: #f5f5f5;
  padding: 16px;
  border-radius: 4px;
  margin-bottom: 16px;
}

.clear-scope-info div {
  margin-bottom: 4px;
}

.detail-row {
  display: flex;
  margin-bottom: 12px;
  align-items: center;
}

.detail-block {
  margin-bottom: 16px;
}

.detail-label {
  font-weight: 500;
  color: rgba(0, 0, 0, 0.85);
  min-width: 80px;
  display: inline-block;
}

.detail-content {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  margin-top: 8px;
  white-space: pre-wrap;
  word-break: break-all;
  font-size: 14px;
  line-height: 1.6;
  max-height: 300px;
  overflow-y: auto;
}

.json-content {
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

.form-item {
  margin-bottom: 16px;
}

.form-item label {
  display: block;
  margin-bottom: 8px;
  color: rgba(0, 0, 0, 0.85);
}

.form-item input,
.form-item textarea,
.form-item select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 24px;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding: 16px;
  background: #fff;
  border-radius: 4px;
}

.pagination-info {
  color: rgba(0, 0, 0, 0.65);
  font-size: 14px;
}

.pagination-controls {
  display: flex;
  gap: 8px;
}

.pagination-controls button {
  padding: 8px 12px;
  min-width: 60px;
}

.pagination-controls button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
