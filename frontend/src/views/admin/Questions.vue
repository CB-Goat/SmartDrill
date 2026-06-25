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

    <div v-if="importDialogVisible" class="modal-overlay">
      <div class="modal-content import-modal" @click.stop>
        <div class="modal-header">
          <h3>题库导入</h3>
          <button v-if="importStatus === 'completed' || importStatus === 'error'" class="close-btn" @click="closeImportDialog">×</button>
        </div>
        <div class="modal-body import-body">
          <div class="import-status">
            <div v-if="importStatus === 'uploading'" class="status-uploading">
              <div class="status-icon">⏳</div>
              <div class="status-text">文件上传中...</div>
            </div>
            <div v-else-if="importStatus === 'processing'" class="status-processing">
              <div class="status-icon">📥</div>
              <div class="status-text">正在导入题库...</div>
            </div>
            <div v-else-if="importStatus === 'completed'" class="status-completed">
              <div class="status-icon">✅</div>
              <div class="status-text">导入完成</div>
            </div>
            <div v-else class="status-error">
              <div class="status-icon">❌</div>
              <div class="status-text">导入失败</div>
            </div>
          </div>

          <div v-if="importProgress.total > 0" class="progress-section">
            <div class="progress-info">
              <span>进度: {{ importProgress.current }} / {{ importProgress.total }}</span>
              <span class="progress-percent">{{ getProgressPercent() }}%</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: getProgressPercent() + '%' }"></div>
            </div>
            <div class="progress-stats">
              <span class="stat-imported">✓ 成功: {{ importProgress.imported }}</span>
              <span class="stat-skipped">⊘ 跳过: {{ importProgress.skipped }}</span>
            </div>
          </div>

          <div v-if="importResult && importResult.skip_reasons" class="result-section">
            <h4>跳过原因统计</h4>
            <div class="reasons-list">
              <div v-for="(count, reason) in importResult.skip_reasons" :key="reason" class="reason-item" v-show="count > 0">
                <span>{{ reason }}</span>
                <span class="reason-count">{{ count }}</span>
              </div>
            </div>
          </div>

          <div v-if="importResult && importResult.skip_details && importResult.skip_details.length > 0" class="result-section">
            <h4>跳过详情 (前{{ importResult.skip_details.length }}条)</h4>
            <ul class="details-list">
              <li v-for="(detail, idx) in importResult.skip_details" :key="idx">{{ detail }}</li>
            </ul>
          </div>

          <div class="logs-section">
            <h4>实时日志</h4>
            <div class="log-container" ref="logContainer">
              <div v-for="(log, idx) in importLogs" :key="idx" class="log-item">{{ log }}</div>
              <div v-if="importLogs.length === 0" class="log-empty">暂无日志</div>
            </div>
          </div>
        </div>
        <div class="form-actions">
          <button v-if="importStatus === 'completed'" type="button" class="btn-primary" @click="closeImportDialog(); loadQuestions();">关闭并刷新</button>
          <button v-else-if="importStatus === 'error'" type="button" class="btn-default" @click="closeImportDialog">关闭</button>
          <button v-else type="button" class="btn-default" @click="closeImportDialog" disabled>导入中...</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { api } from '@/api'
import axios from 'axios'

const questions = ref<any[]>([])
const viewVisible = ref(false)
const currentQuestion = ref<any>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const importing = ref(false)
const clearConfirmVisible = ref(false)
const clearing = ref(false)

const importDialogVisible = ref(false)
const importStatus = ref<'uploading' | 'processing' | 'completed' | 'error'>('uploading')
const importProgress = ref({
  current: 0,
  total: 0,
  imported: 0,
  skipped: 0
})
const importLogs = ref<string[]>([])
const importResult = ref<any>(null)
const importLastReason = ref<string>('')
const logContainer = ref<HTMLElement | null>(null)

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

  importDialogVisible.value = true
  importStatus.value = 'uploading'
  importProgress.value = {
    current: 0,
    total: 0,
    imported: 0,
    skipped: 0
  }
  importLogs.value = []
  importResult.value = null

  try {
    const formData = new FormData()
    formData.append('file', file)

    const adminToken = localStorage.getItem('admin_token')

    const xhr = new XMLHttpRequest()
    xhr.open('POST', '/api/admin/import-questions', true)
    xhr.setRequestHeader('Authorization', `Bearer ${adminToken}`)

    importStatus.value = 'processing'

    xhr.onprogress = () => {}

    xhr.onreadystatechange = () => {
      if (xhr.readyState === 3 || xhr.readyState === 4) {
        const lines = xhr.responseText.split('\n')
        for (const line of lines) {
          if (line.startsWith('data:')) {
            const data = line.substring(5).trim()
            if (!data) continue
            try {
              const event = JSON.parse(data)
              handleImportEvent(event)
            } catch (e) {
              console.error('解析SSE数据失败:', e, data)
            }
          }
        }
      }
    }

    xhr.onload = () => {
      if (xhr.status === 200) {
        if (importStatus.value === 'processing') {
          importStatus.value = 'completed'
        }
      } else {
        importStatus.value = 'error'
        importLogs.value.push(`错误: HTTP ${xhr.status}`)
      }
    }

    xhr.onerror = () => {
      importStatus.value = 'error'
      importLogs.value.push('网络错误，上传失败')
    }

    xhr.send(formData)
  } catch (error: any) {
    importStatus.value = 'error'
    importLogs.value.push('错误: ' + (error.message || '未知错误'))
  } finally {
    if (target) target.value = ''
  }
}

function handleImportEvent(event: any) {
  if (event.total !== undefined && importProgress.value.total === 0) {
    importProgress.value.total = event.total
    addLog(`开始处理，共 ${event.total} 行数据`)
  }

  if (event.current !== undefined) {
    importProgress.value.current = event.current
    importProgress.value.imported = event.imported || 0
    importProgress.value.skipped = event.skipped || 0

    if (event.reason && event.reason !== importLastReason.value) {
      addLog(`第 ${event.current} 行: ${event.reason}`)
      importLastReason.value = event.reason
    }
  }

  if (event.message && event.imported !== undefined) {
    importResult.value = event
    importStatus.value = 'completed'
    addLog(`导入完成: 成功 ${event.imported}, 跳过 ${event.skipped}`)
  }
}

function addLog(message: string) {
  const timestamp = new Date().toLocaleTimeString()
  importLogs.value.push(`[${timestamp}] ${message}`)
  if (importLogs.value.length > 200) {
    importLogs.value = importLogs.value.slice(-200)
  }
  nextTick(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = logContainer.value.scrollHeight
    }
  })
}

function closeImportDialog() {
  importDialogVisible.value = false
}

function getProgressPercent(): number {
  if (importProgress.value.total === 0) return 0
  return Math.round((importProgress.value.current / importProgress.value.total) * 100)
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

.import-modal {
  width: 700px;
  max-height: 85vh;
}

.import-body {
  padding: 0;
}

.import-status {
  text-align: center;
  padding: 24px 0;
  border-bottom: 1px solid #f0f0f0;
}

.status-icon {
  font-size: 48px;
  margin-bottom: 8px;
}

.status-text {
  font-size: 18px;
  color: rgba(0, 0, 0, 0.85);
}

.status-completed .status-text {
  color: #52c41a;
}

.status-error .status-text {
  color: #ff4d4f;
}

.progress-section {
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  color: rgba(0, 0, 0, 0.65);
}

.progress-percent {
  color: #1890ff;
  font-weight: 500;
}

.progress-bar {
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #1890ff, #36cfc9);
  transition: width 0.3s ease;
}

.progress-stats {
  display: flex;
  gap: 24px;
  margin-top: 12px;
  font-size: 14px;
}

.stat-imported {
  color: #52c41a;
}

.stat-skipped {
  color: #fa8c16;
}

.result-section {
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
}

.result-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.85);
}

.reasons-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.reason-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background: #fafafa;
  border-radius: 4px;
  font-size: 13px;
}

.reason-count {
  color: #ff4d4f;
  font-weight: 500;
}

.details-list {
  margin: 0;
  padding-left: 20px;
  max-height: 200px;
  overflow-y: auto;
  font-size: 13px;
  color: rgba(0, 0, 0, 0.65);
}

.details-list li {
  margin-bottom: 4px;
}

.logs-section {
  padding: 16px 0 0 0;
}

.logs-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.85);
}

.log-container {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 12px;
  border-radius: 4px;
  height: 200px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.6;
}

.log-item {
  white-space: pre-wrap;
  word-break: break-all;
}

.log-empty {
  color: #888;
  font-style: italic;
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
