<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px">
      <h2 style="margin: 0">知识考点管理</h2>
      <div>
        <button class="btn-default" @click="showImport = true" style="margin-right: 8px">Excel导入</button>
        <button class="btn-default" @click="cleanDuplicates" style="margin-right: 8px">清理重复</button>
        <button class="btn-primary" @click="openAdd">添加知识考点</button>
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
      <select v-model="filterSemesterId" @change="onSemesterChange">
        <option v-for="sem in filteredSemesters" :key="sem.id" :value="sem.id">{{ sem.name }}</option>
      </select>
      <select v-model="filterUnitId" @change="onLoad">
        <option v-for="u in filteredUnits" :key="u.id" :value="u.id">{{ u.name }}</option>
      </select>
    </div>
    
    <div v-for="item in items" :key="item.id" class="knowledge-card">
      <div class="knowledge-header">
        <h3>{{ item.title }}</h3>
        <button class="btn-link" @click="editItem(item)">编辑</button>
      </div>
      <div class="knowledge-content">{{ item.content }}</div>
      <div v-if="item.exam_points && item.exam_points.length > 0" class="exam-points">
        <div class="exam-points-title">考点列表：</div>
        <div v-for="ep in item.exam_points" :key="ep.id" class="exam-point-item">
          <div class="exam-point-header">
            <span class="exam-point-title">{{ ep.title }}</span>
            <span class="exam-point-badge" :class="'freq-' + ep.exam_frequency">{{ ep.exam_frequency }}</span>
          </div>
          <div class="exam-point-content">{{ ep.content }}</div>
          <div v-if="ep.exam_types" class="exam-point-types">题型：{{ ep.exam_types }}</div>
        </div>
      </div>
    </div>
    
    <div v-if="showForm" class="modal-overlay" @click="showForm = false">
      <div class="modal-content" @click.stop>
        <h3>{{ form.id ? '编辑知识考点' : '添加知识考点' }}</h3>
        <form @submit.prevent="onSubmit">
          <div class="form-item">
            <label>单元</label>
            <select v-model="form.unit_id" required>
              <option v-for="u in filteredUnits" :key="u.id" :value="u.id">{{ u.name }}</option>
            </select>
          </div>
          <div class="form-item">
            <label>知识点标题</label>
            <input v-model="form.title" required />
          </div>
          <div class="form-item">
            <label>知识点内容</label>
            <textarea v-model="form.content" rows="5"></textarea>
          </div>
          <div class="form-item">
            <label>考点（每行一个，格式：标题|内容|题型|频率）</label>
            <textarea v-model="examPointsText" rows="5" placeholder="字音辨析|易读错的字|选择题|常考"></textarea>
          </div>
          <div class="form-actions">
            <button type="button" class="btn-default" @click="showForm = false">取消</button>
            <button type="submit" class="btn-primary">保存</button>
          </div>
        </form>
      </div>
    </div>
    
    <div v-if="showImport" class="modal-overlay" @click="showImport = false">
      <div class="modal-content" @click.stop>
        <h3>Excel导入</h3>
        <div class="form-item">
          <label>选择Excel文件（每个科目一个Sheet）</label>
          <input type="file" accept=".xlsx,.xls" @change="handleFileChange" />
        </div>
        <div class="import-tips">
          <p>Excel格式要求：</p>
          <p>A列：年级 | B列：学期 | C列：单元编号 | D列：单元名称</p>
          <p>E列：知识点 | F列：考点 | G列：常见题型 | H列：考试频率</p>
        </div>
        <div class="form-actions">
          <button type="button" class="btn-default" @click="showImport = false">取消</button>
          <button type="button" class="btn-primary" @click="doImport" :disabled="!importFile">导入</button>
        </div>
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
const units = ref<any[]>([])
const showForm = ref(false)
const showImport = ref(false)
const importFile = ref<File | null>(null)
const examPointsText = ref('')

const filterVersionId = ref(1)
const filterGradeId = ref(1)
const filterSubjectId = ref(1)
const filterSemesterId = ref(1)
const filterUnitId = ref(1)

const form = reactive({ id: 0, unit_id: 1, title: '', content: '' })

const filteredGrades = computed(() => grades.value.filter(g => g.version_id === filterVersionId.value))
const filteredSubjects = computed(() => subjects.value.filter(s => s.grade_id === filterGradeId.value))
const filteredSemesters = computed(() => semesters.value.filter(sem => sem.subject_id === filterSubjectId.value))
const filteredUnits = computed(() => units.value.filter(u => u.semester_id === filterSemesterId.value))

async function onLoad() {
  versions.value = await api.admin.getVersions()
  grades.value = await api.admin.getGrades()
  subjects.value = await api.admin.getSubjects()
  semesters.value = await api.admin.getSemesters()
  units.value = await api.admin.getUnits()
  
  if (filteredGrades.value.length > 0 && !filteredGrades.value.find(g => g.id === filterGradeId.value)) {
    filterGradeId.value = filteredGrades.value[0].id
  }
  if (filteredSubjects.value.length > 0 && !filteredSubjects.value.find(s => s.id === filterSubjectId.value)) {
    filterSubjectId.value = filteredSubjects.value[0].id
  }
  if (filteredSemesters.value.length > 0 && !filteredSemesters.value.find(sem => sem.id === filterSemesterId.value)) {
    filterSemesterId.value = filteredSemesters.value[0].id
  }
  if (filteredUnits.value.length > 0 && !filteredUnits.value.find(u => u.id === filterUnitId.value)) {
    filterUnitId.value = filteredUnits.value[0].id
  }
  
  items.value = await api.admin.getKnowledgeExamPoints(filterUnitId.value)
}

function onVersionChange() {
  if (filteredGrades.value.length > 0) filterGradeId.value = filteredGrades.value[0].id
  onGradeChange()
}

function onGradeChange() {
  if (filteredSubjects.value.length > 0) filterSubjectId.value = filteredSubjects.value[0].id
  onSubjectChange()
}

function onSubjectChange() {
  if (filteredSemesters.value.length > 0) filterSemesterId.value = filteredSemesters.value[0].id
  onSemesterChange()
}

function onSemesterChange() {
  if (filteredUnits.value.length > 0) filterUnitId.value = filteredUnits.value[0].id
  onLoad()
}

function openAdd() {
  Object.assign(form, { id: 0, unit_id: filterUnitId.value, title: '', content: '' })
  examPointsText.value = ''
  showForm.value = true
}

function editItem(item: any) {
  Object.assign(form, item)
  examPointsText.value = (item.exam_points || []).map((ep: any) => 
    `${ep.title}|${ep.content}|${ep.exam_types || ''}|${ep.exam_frequency || '常考'}`
  ).join('\n')
  showForm.value = true
}

async function onSubmit() {
  const examPoints = examPointsText.value.split('\n').filter(line => line.trim()).map(line => {
    const parts = line.split('|')
    return {
      title: parts[0] || '',
      content: parts[1] || '',
      exam_types: parts[2] || '',
      exam_frequency: parts[3] || '常考'
    }
  })
  
  await api.admin.saveKnowledgeExamPoint({ ...form, exam_points: examPoints })
  showForm.value = false
  onLoad()
}

function handleFileChange(e: any) {
  importFile.value = e.target.files[0]
}

async function doImport() {
  if (!importFile.value) return
  
  const formData = new FormData()
  formData.append('file', importFile.value)
  
  try {
    const response = await fetch('/api/admin/import-knowledge-exam-points', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + localStorage.getItem('admin_token')
      },
      body: formData
    })
    
    const result = await response.json()
    alert(result.message)
    showImport.value = false
    importFile.value = null
    onLoad()
  } catch (error) {
    alert('导入失败')
  }
}

async function cleanDuplicates() {
  if (!confirm('确定清理重复考点吗？')) return
  
  try {
    const response = await fetch('/api/admin/clean-duplicate-exam-points', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + localStorage.getItem('admin_token')
      }
    })
    
    const result = await response.json()
    alert(result.message)
    onLoad()
  } catch (error) {
    alert('清理失败')
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

.knowledge-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.knowledge-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.knowledge-header h3 {
  margin: 0;
  color: #333;
}

.knowledge-content {
  color: #666;
  margin-bottom: 16px;
  white-space: pre-wrap;
}

.exam-points {
  border-top: 1px solid #f0f0f0;
  padding-top: 16px;
}

.exam-points-title {
  font-weight: bold;
  margin-bottom: 12px;
  color: #333;
}

.exam-point-item {
  background: #fafafa;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 8px;
}

.exam-point-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.exam-point-title {
  font-weight: 500;
  color: #333;
}

.exam-point-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.freq-少考 {
  background: #e6f7ff;
  color: #1890ff;
}

.freq-常考 {
  background: #fff7e6;
  color: #fa8c16;
}

.freq-必考 {
  background: #fff1f0;
  color: #f5222d;
}

.exam-point-content {
  color: #666;
  margin-bottom: 8px;
  white-space: pre-wrap;
}

.exam-point-types {
  color: #999;
  font-size: 12px;
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