<template>
  <div class="home-page">
    <div class="header-bar">
      <div class="welcome-section">
        <span class="welcome-text">欢迎回来，</span>
        <span class="user-name">{{ userStore.userInfo?.username || '用户' }}</span>
      </div>
      <div class="points-section">
        <span class="points-text">我的积分：{{ userStore.userInfo?.points || 0 }}</span>
        <router-link to="/recharge" class="recharge-btn">充值</router-link>
      </div>
    </div>
    
    <div class="main-content">
      <div class="card">
        <div class="top-tabs">
          <div class="grade-semester-tab" @click="showGradeSelector = true">
            <span>{{ currentGradeName }}{{ currentSemester }}</span>
            <van-icon name="arrow-down" size="12" style="margin-left: 4px" />
          </div>
          
          <div class="type-tabs">
            <div 
              :class="['type-tab', 'review-tab', { active: activeType === 'review' }]"
              @click="activeType = 'review'"
            >
              单元复习
            </div>
            <div 
              :class="['type-tab', 'practice-tab', { active: activeType === 'practice' }]"
              @click="activeType = 'practice'"
            >
              训练刷题
            </div>
          </div>
        </div>
        
        <div class="card-body">
          <div class="subject-tabs">
            <div 
              v-for="(subject, index) in subjects" 
              :key="subject.subject_id"
              :class="['subject-tab', { active: activeSubject === index }]"
              @click="activeSubject = index"
            >
              <div class="subject-name">{{ subject.subject_name }}</div>
            </div>
          </div>
          
          <div class="units-container">
            <div v-if="currentSubject" class="units-list">
              <span 
                v-for="unit in currentSubject.units" 
                :key="unit.id" 
                :class="['unit-link', { 'unit-downloaded': isDownloaded(unit) }]"
                @click="handleUnitClick(unit)"
              >
                {{ unit.name }}
                <span v-if="activeType === 'practice' && unit.question_count" class="unit-qcount">{{ unit.question_count }}题</span>
              </span>
            </div>
            <div v-else class="empty-text">暂无资料</div>
          </div>
        </div>
      </div>
    </div>
    
    <van-popup v-model:show="showGradeSelector" position="bottom" round>
      <div class="grade-selector">
        <div class="selector-header">
          <span>选择年级和学期</span>
          <van-icon name="cross" @click="showGradeSelector = false" />
        </div>
        <div class="selector-body">
          <div class="selector-section">
            <div class="section-title">年级</div>
            <div class="grade-list">
              <div 
                v-for="grade in allGrades" 
                :key="grade.id"
                :class="['grade-item', { active: selectedGradeId === grade.id }]"
                @click="selectedGradeId = grade.id"
              >
                {{ grade.name }}
              </div>
            </div>
          </div>
          <div class="selector-section">
            <div class="section-title">学期</div>
            <div class="semester-list">
              <div 
                :class="['semester-item', { active: selectedSemester === '上册' }]"
                @click="selectedSemester = '上册'"
              >
                上册
              </div>
              <div 
                :class="['semester-item', { active: selectedSemester === '下册' }]"
                @click="selectedSemester = '下册'"
              >
                下册
              </div>
            </div>
          </div>
        </div>
        <div class="selector-footer">
          <van-button type="primary" block @click="confirmGradeChange">确定</van-button>
        </div>
      </div>
    </van-popup>
    
    <div v-if="previewVisible" class="modal-overlay" @click="previewVisible = false">
      <div class="modal-content" @click.stop>
        <div class="modal-body" ref="previewContainer"></div>
        <div class="modal-footer">
          <button class="btn-close" @click="previewVisible = false">关闭（×）</button>
          <button class="btn-primary" @click="downloadUnit">下载Word（10积分）</button>
        </div>
      </div>
    </div>
    
    <div v-if="paperConfigVisible" class="modal-overlay" @click="paperConfigVisible = false">
      <div class="modal-content paper-config-modal" @click.stop>
        <div class="modal-header">
          <span class="modal-title">{{ currentPaperUnit?.name }} - 试卷配置</span>
        </div>
        <div class="modal-body paper-config-body">
          <div class="config-item">
            <label>试卷总题数：{{ totalSelectedCount }} / {{ paperQuestionCount }} <span class="points-cost">（消耗 {{ paperQuestionCount }} 积分）</span></label>
            <div class="qty-selector">
              <button class="qty-btn" @click="paperQuestionCount > 1 && adjustTotalQuestionCount(paperQuestionCount - 1)">-</button>
              <input type="number" :value="paperQuestionCount" @change="handleTotalQuestionCountChange" :max="maxQuestionCount" />
              <button class="qty-btn" @click="paperQuestionCount < maxQuestionCount && adjustTotalQuestionCount(paperQuestionCount + 1)">+</button>
            </div>
            <span class="config-hint">该单元共 {{ maxQuestionCount }} 道题</span>
          </div>
          
          <div class="config-item">
            <label>难度分配（共 {{ totalDifficultyCount }} 题）</label>
            <div class="distribution-list">
              <div v-for="d in difficultyList" :key="d.id" class="distribution-item">
                <span class="dist-name">{{ d.name }}</span>
                <span class="dist-total">（{{ d.count }}题）</span>
                <div class="qty-selector">
                  <button class="qty-btn" @click="adjustDifficultyCount(d.id, -1)">-</button>
                  <input type="number" :value="getDifficultyCount(d.id)" @change="(e) => setDifficultyCount(d.id, Number((e.target as HTMLInputElement).value))" :max="d.count" />
                  <button class="qty-btn" @click="adjustDifficultyCount(d.id, 1)">+</button>
                </div>
              </div>
            </div>
          </div>
          
          <div class="config-item">
            <label>题型分配（共 {{ totalQuestionTypeCount }} 题）</label>
            <div class="distribution-list">
              <div v-for="t in questionTypeList" :key="t.id" class="distribution-item">
                <span class="dist-name">{{ t.name }}</span>
                <span class="dist-total">（{{ t.count }}题）</span>
                <div class="qty-selector">
                  <button class="qty-btn" @click="adjustQuestionTypeCount(t.id, -1)">-</button>
                  <input type="number" :value="getQuestionTypeCount(t.id)" @change="(e) => setQuestionTypeCount(t.id, Number((e.target as HTMLInputElement).value))" :max="t.count" />
                  <button class="qty-btn" @click="adjustQuestionTypeCount(t.id, 1)">+</button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-close" @click="paperConfigVisible = false">取消</button>
          <button class="btn-primary" @click="generatePaperPreview" :disabled="generatingPaper">
            {{ generatingPaper ? '生成中...' : '生成试卷' }}
          </button>
        </div>
      </div>
    </div>
    
    <div v-if="paperPreviewVisible" class="modal-overlay" @click="paperPreviewVisible = false">
      <div class="modal-content" @click.stop>
        <div class="modal-body" ref="paperPreviewContainer"></div>
        <div class="modal-footer">
          <button class="btn-close" @click="paperPreviewVisible = false">关闭（×）</button>
          <button class="btn-primary" @click="downloadPaper">下载试卷（{{ paperData?.question_count || 0 }} 积分）</button>
        </div>
      </div>
    </div>
    
    <van-tabbar v-model="activeTabbar" active-color="#ff6b6b" inactive-color="#999">
      <van-tabbar-item icon="home-o" to="/">首页</van-tabbar-item>
      <van-tabbar-item icon="description" to="/orders">订单</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/profile">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { showToast } from 'vant'

const userStore = useUserStore()
const activeTabbar = ref(0)
const activeType = ref<'review' | 'practice'>('review')
const activeSubject = ref(0)
const subjects = ref<any[]>([])

const currentGradeName = ref('')
const currentSemester = ref('')
const currentGradeId = ref<number | null>(null)
const allGrades = ref<any[]>([])

const showGradeSelector = ref(false)
const selectedGradeId = ref<number | null>(null)
const selectedSemester = ref('')

const previewVisible = ref(false)
const previewUnitData = ref<any>(null)
const previewContainer = ref<HTMLElement | null>(null)

const paperConfigVisible = ref(false)
const paperPreviewVisible = ref(false)
const currentPaperUnit = ref<any>(null)
const paperQuestionCount = ref(10)
const difficultyList = ref<any[]>([])
const questionTypeList = ref<any[]>([])
const maxQuestionCount = ref(0)
const generatingPaper = ref(false)
const paperPreviewContainer = ref<HTMLElement | null>(null)
const paperData = ref<any>(null)

const difficultyCounts = ref<Record<number, number>>({})
const questionTypeCounts = ref<Record<number, number>>({})

const totalDifficultyCount = computed(() => {
  return Object.values(difficultyCounts.value).reduce((sum, count) => sum + count, 0)
})

const totalQuestionTypeCount = computed(() => {
  return Object.values(questionTypeCounts.value).reduce((sum, count) => sum + count, 0)
})

const totalSelectedCount = computed(() => {
  return Math.max(totalDifficultyCount.value, totalQuestionTypeCount.value)
})

const currentSubject = computed(() => subjects.value[activeSubject.value] || null)

function isDownloaded(unit: any) {
  return activeType.value === 'review' ? unit.review_downloaded : unit.practice_downloaded
}

async function handleUnitClick(unit: any) {
  if (activeType.value === 'review') {
    await previewUnit(unit)
  } else {
    await openPaperConfig(unit)
  }
}

async function openPaperConfig(unit: any) {
  try {
    currentPaperUnit.value = unit
    paperQuestionCount.value = 10
    difficultyCounts.value = {}
    questionTypeCounts.value = {}
    
    const response = await fetch(`/api/user/unit-question-stats/${unit.id}`, {
      headers: { 'Authorization': 'Bearer ' + userStore.token }
    })
    const result = await response.json()
    
    maxQuestionCount.value = result.total || 0
    difficultyList.value = (result.difficulty_stats || []).filter((d: any) => d.count > 0)
    questionTypeList.value = (result.type_stats || []).filter((t: any) => t.count > 0)
    
    if (maxQuestionCount.value > 0 && paperQuestionCount.value > maxQuestionCount.value) {
      paperQuestionCount.value = maxQuestionCount.value
    }
    
    autoDistributeCounts()
    
    paperConfigVisible.value = true
  } catch (error) {
    showToast('获取题库信息失败')
  }
}

const BIG_QUESTION_TYPES = ['作文题', '应用题', '解答题', '计算题']

function getQuestionTypeMaxLimit(typeName: string, totalCount: number): number {
  if (typeName.includes('作文')) {
    return 1
  }
  if (BIG_QUESTION_TYPES.some(t => typeName.includes(t))) {
    return Math.max(1, Math.floor(totalCount / 5))
  }
  return totalCount
}

function getCommonQuestionTypes() {
  const commonTypes = ['单选题', '多选题', '填空题', '判断题']
  return questionTypeList.value.filter(t => 
    commonTypes.some(ct => t.name.includes(ct))
  )
}

function autoDistributeCounts() {
  difficultyCounts.value = {}
  questionTypeCounts.value = {}
  
  const count = paperQuestionCount.value
  
  if (difficultyList.value.length > 0) {
    const avg = Math.floor(count / difficultyList.value.length)
    const remainder = count % difficultyList.value.length
    
    difficultyList.value.forEach((d, index) => {
      const maxAllowed = Math.min(d.count, index < remainder ? avg + 1 : avg)
      difficultyCounts.value[d.id] = maxAllowed > 0 ? maxAllowed : 0
    })
  }
  
  if (questionTypeList.value.length > 0) {
    questionTypeList.value.forEach(t => {
      questionTypeCounts.value[t.id] = 0
    })
    
    let remaining = count
    
    const bigTypes = questionTypeList.value.filter(t => 
      BIG_QUESTION_TYPES.some(bt => t.name.includes(bt)) || t.name.includes('作文')
    )
    
    bigTypes.forEach(t => {
      const maxLimit = getQuestionTypeMaxLimit(t.name, count)
      const maxAllowed = Math.min(t.count, maxLimit)
      const assignCount = Math.min(remaining, maxAllowed)
      questionTypeCounts.value[t.id] = assignCount
      remaining -= assignCount
    })
    
    const commonTypes = questionTypeList.value.filter(t => 
      !BIG_QUESTION_TYPES.some(bt => t.name.includes(bt)) && !t.name.includes('作文')
    )
    
    if (commonTypes.length > 0 && remaining > 0) {
      const avg = Math.floor(remaining / commonTypes.length)
      const remainder = remaining % commonTypes.length
      
      commonTypes.forEach((t, index) => {
        const maxAllowed = Math.min(t.count - (questionTypeCounts.value[t.id] || 0), index < remainder ? avg + 1 : avg)
        questionTypeCounts.value[t.id] = (questionTypeCounts.value[t.id] || 0) + (maxAllowed > 0 ? maxAllowed : 0)
      })
    }
  }
}

function adjustTotalQuestionCount(newCount: number) {
  paperQuestionCount.value = Math.max(1, Math.min(newCount, maxQuestionCount.value))
  autoDistributeCounts()
}

function handleTotalQuestionCountChange(event: any) {
  const newCount = Math.max(1, Math.min(Number(event.target.value) || 1, maxQuestionCount.value))
  paperQuestionCount.value = newCount
  autoDistributeCounts()
}

function getDifficultyCount(id: number) {
  return difficultyCounts.value[id] || 0
}

function setDifficultyCount(id: number, count: number) {
  const diff = difficultyList.value.find(d => d.id === id)
  const maxAllowed = diff ? diff.count : 0
  const adjusted = Math.max(0, Math.min(count, maxAllowed))
  difficultyCounts.value[id] = adjusted
}

function adjustDifficultyCount(id: number, delta: number) {
  const current = difficultyCounts.value[id] || 0
  const diff = difficultyList.value.find(d => d.id === id)
  const maxAllowed = diff ? diff.count : 0
  const newCount = Math.max(0, Math.min(current + delta, maxAllowed))
  difficultyCounts.value[id] = newCount
}

function getQuestionTypeCount(id: number) {
  return questionTypeCounts.value[id] || 0
}

function setQuestionTypeCount(id: number, count: number) {
  const qt = questionTypeList.value.find(t => t.id === id)
  if (!qt) return
  
  const maxLimit = getQuestionTypeMaxLimit(qt.name, paperQuestionCount.value)
  const maxAllowed = Math.min(qt.count, maxLimit)
  const adjusted = Math.max(0, Math.min(count, maxAllowed))
  
  const diff = adjusted - (questionTypeCounts.value[id] || 0)
  questionTypeCounts.value[id] = adjusted
  
  if (diff !== 0) {
    redistributeQuestionTypeCount(diff, id)
  }
}

function adjustQuestionTypeCount(id: number, delta: number) {
  const current = questionTypeCounts.value[id] || 0
  const qt = questionTypeList.value.find(t => t.id === id)
  if (!qt) return
  
  const maxLimit = getQuestionTypeMaxLimit(qt.name, paperQuestionCount.value)
  const maxAllowed = Math.min(qt.count, maxLimit)
  const newCount = Math.max(0, Math.min(current + delta, maxAllowed))
  
  const diff = newCount - current
  questionTypeCounts.value[id] = newCount
  
  if (diff !== 0) {
    redistributeQuestionTypeCount(diff, id)
  }
}

function redistributeQuestionTypeCount(diff: number, excludeId: number) {
  if (diff === 0) return
  
  const commonTypes = getCommonQuestionTypes().filter(t => t.id !== excludeId)
  
  if (commonTypes.length === 0) {
    commonTypes.push(...questionTypeList.value.filter(t => t.id !== excludeId))
  }
  
  if (commonTypes.length === 0) return
  
  const absDiff = Math.abs(diff)
  
  if (diff < 0) {
    let remaining = absDiff
    
    commonTypes.forEach(t => {
      if (remaining <= 0) return
      
      const maxLimit = getQuestionTypeMaxLimit(t.name, paperQuestionCount.value)
      const available = Math.min(t.count, maxLimit) - (questionTypeCounts.value[t.id] || 0)
      const add = Math.min(remaining, available)
      
      if (add > 0) {
        questionTypeCounts.value[t.id] = (questionTypeCounts.value[t.id] || 0) + add
        remaining -= add
      }
    })
  } else {
    let remaining = absDiff
    
    commonTypes.forEach(t => {
      if (remaining <= 0) return
      
      const current = questionTypeCounts.value[t.id] || 0
      const remove = Math.min(remaining, current)
      
      if (remove > 0) {
        questionTypeCounts.value[t.id] = current - remove
        remaining -= remove
      }
    })
  }
}

async function generatePaperPreview() {
  if (!currentPaperUnit.value) return
  
  if (totalSelectedCount.value !== paperQuestionCount.value) {
    showToast('难度和题型分配的题数总和必须等于试卷总题数')
    return
  }
  
  try {
    generatingPaper.value = true
    
    const params = new URLSearchParams()
    params.append('question_count', paperQuestionCount.value.toString())
    
    Object.entries(difficultyCounts.value).forEach(([id, count]) => {
      if (count > 0) {
        params.append(`difficulty_${id}`, count.toString())
      }
    })
    
    Object.entries(questionTypeCounts.value).forEach(([id, count]) => {
      if (count > 0) {
        params.append(`type_${id}`, count.toString())
      }
    })
    
    const url = `/api/user/paper-word/${currentPaperUnit.value.id}?${params.toString()}`
    
    const response = await fetch(url, {
      headers: { 'Authorization': 'Bearer ' + userStore.token }
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || '生成试卷失败')
    }
    
    const blob = await response.blob()
    
    paperData.value = {
      unit_id: currentPaperUnit.value.id,
      unit_name: currentPaperUnit.value.name,
      question_count: paperQuestionCount.value,
      difficulty_counts: { ...difficultyCounts.value },
      question_type_counts: { ...questionTypeCounts.value },
      order_id: null
    }
    
    paperConfigVisible.value = false
    paperPreviewVisible.value = true
    
    setTimeout(async () => {
      if (paperPreviewContainer.value) {
        const { renderAsync } = await import('docx-preview')
        paperPreviewContainer.value.innerHTML = ''
        
        await renderAsync(blob, paperPreviewContainer.value, undefined, {
          className: 'docx-preview-wrapper',
          inWrapper: true,
          ignoreWidth: true,
          ignoreHeight: false,
          ignoreFonts: false,
          breakPages: true,
          ignoreLastRenderedPageBreak: true,
          experimental: false,
          trimXmlDeclaration: true,
          useBase64URL: true,
          renderHeaders: true,
          renderFooters: true,
          renderFootnotes: true,
          renderEndnotes: true
        })
      }
    }, 100)
  } catch (error: any) {
    showToast(error.message || '生成试卷失败')
  } finally {
    generatingPaper.value = false
  }
}

async function downloadPaper() {
  if (!paperData.value) return
  
  try {
    const response = await fetch(`/api/user/download-paper/${paperData.value.unit_id}`, {
      method: 'POST',
      headers: { 
        'Authorization': 'Bearer ' + userStore.token,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        question_count: paperData.value.question_count,
        difficulty_counts: paperData.value.difficulty_counts,
        question_type_counts: paperData.value.question_type_counts
      })
    })
    
    const result = await response.json()
    
    if (!response.ok) {
      showToast(result.detail || '下载失败')
      return
    }
    
    paperData.value.order_id = result.order_id
    
    if (result.saved) {
      showToast('下载成功（已保存）')
    } else {
      userStore.userInfo.points = result.points
      showToast(`下载成功，已扣${paperData.value.question_count}积分`)
    }
    
    let url
    if (result.saved && result.order_id) {
      url = `/api/user/saved-paper/${result.order_id}`
    } else {
      const params = new URLSearchParams()
      params.append('question_count', paperData.value.question_count.toString())
      
      Object.entries(paperData.value.difficulty_counts || {}).forEach(([id, count]) => {
        if (count > 0) {
          params.append(`difficulty_${id}`, count.toString())
        }
      })
      
      Object.entries(paperData.value.question_type_counts || {}).forEach(([id, count]) => {
        if (count > 0) {
          params.append(`type_${id}`, count.toString())
        }
      })
      
      url = `/api/user/paper-word/${paperData.value.unit_id}?${params.toString()}`
    }
    
    const wordResponse = await fetch(url, {
      headers: { 'Authorization': 'Bearer ' + userStore.token }
    })
    const blob = await wordResponse.blob()
    const urlObj = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = urlObj
    a.download = `${paperData.value.unit_name} - 单元测试卷.docx`
    a.click()
    window.URL.revokeObjectURL(urlObj)
    
    paperPreviewVisible.value = false
  } catch (error) {
    showToast('下载失败')
  }
}

onMounted(async () => {
  await userStore.fetchUserInfo()
  await loadHomeData()
})

async function loadHomeData(gradeId?: number, semester?: string) {
  try {
    let url = '/api/user/home-data'
    const params = new URLSearchParams()
    if (gradeId) params.append('grade_id', gradeId.toString())
    if (semester) params.append('semester', semester)
    if (params.toString()) url += '?' + params.toString()
    
    const response = await fetch(url, {
      headers: { 'Authorization': 'Bearer ' + userStore.token }
    })
    const result = await response.json()
    subjects.value = result.subjects || []
    currentGradeName.value = result.grade_name || ''
    currentSemester.value = result.semester || ''
    currentGradeId.value = result.current_grade_id
    allGrades.value = result.all_grades || []
    
    selectedGradeId.value = result.current_grade_id
    selectedSemester.value = result.semester || ''
  } catch (error) {
    console.error('加载数据失败')
  }
}

async function confirmGradeChange() {
  if (!selectedGradeId.value) {
    showToast('请选择年级')
    return
  }
  
  showGradeSelector.value = false
  activeSubject.value = 0
  await loadHomeData(selectedGradeId.value, selectedSemester.value)
}

async function previewUnit(unit: any) {
  try {
    const response = await fetch(`/api/user/unit-word/${unit.id}`, {
      headers: { 'Authorization': 'Bearer ' + userStore.token }
    })
    
    if (!response.ok) {
      throw new Error('预览失败')
    }
    
    const blob = await response.blob()
    
    previewUnitData.value = {
      unit_id: unit.id,
      unit_name: unit.name
    }
    previewVisible.value = true
    
    setTimeout(async () => {
      if (previewContainer.value) {
        const { renderAsync } = await import('docx-preview')
        previewContainer.value.innerHTML = ''
        
        await renderAsync(blob, previewContainer.value, undefined, {
          className: 'docx-preview-wrapper',
          inWrapper: true,
          ignoreWidth: true,
          ignoreHeight: false,
          ignoreFonts: false,
          breakPages: true,
          ignoreLastRenderedPageBreak: true,
          experimental: false,
          trimXmlDeclaration: true,
          useBase64URL: true,
          renderHeaders: true,
          renderFooters: true,
          renderFootnotes: true,
          renderEndnotes: true
        })
      }
    }, 100)
  } catch (error) {
    showToast('预览失败')
  }
}

async function downloadUnit() {
  if (!previewUnitData.value) return
  
  try {
    const response = await fetch(`/api/user/download-unit/${previewUnitData.value.unit_id}`, {
      method: 'POST',
      headers: { 'Authorization': 'Bearer ' + userStore.token }
    })
    
    const result = await response.json()
    
    if (!response.ok) {
      showToast(result.detail || '下载失败')
      return
    }
    
    userStore.userInfo.points = result.points
    showToast('下载成功，已扣10积分')
    
    const wordResponse = await fetch(`/api/user/unit-word/${previewUnitData.value.unit_id}`, {
      headers: { 'Authorization': 'Bearer ' + userStore.token }
    })
    const blob = await wordResponse.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${previewUnitData.value.unit_name}.docx`
    a.click()
    window.URL.revokeObjectURL(url)
    
    previewVisible.value = false
  } catch (error) {
    showToast('下载失败')
  }
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 60px;
}

.header-bar {
  background: linear-gradient(135deg, #ff6b6b 0%, #ff8e8e 100%);
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #fff;
}

.welcome-section {
  font-size: 16px;
}

.welcome-text {
  opacity: 0.9;
}

.user-name {
  font-weight: bold;
}

.points-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.points-text {
  font-size: 14px;
}

.recharge-btn {
  background: #fff;
  color: #ff6b6b;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
  text-decoration: none;
  font-weight: bold;
}

.main-content {
  padding: 20px;
}

.card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.top-tabs {
  display: flex;
  flex-direction: column;
}

.grade-semester-tab {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  padding: 12px 0;
  text-align: center;
  font-size: 15px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.type-tabs {
  display: flex;
  width: 100%;
}

.type-tab {
  flex: 1;
  padding: 12px 0;
  text-align: center;
  font-size: 15px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  color: #fff;
}

.review-tab {
  background: linear-gradient(135deg, #d3d3d3 0%, #a8a8a8 100%);
}

.practice-tab {
  background: linear-gradient(135deg, #d3d3d3 0%, #a8a8a8 100%);
}

.review-tab.active {
  background: linear-gradient(135deg, #ff6b6b 0%, #ff8e8e 100%);
}

.practice-tab.active {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.card-body {
  display: flex;
  min-height: 400px;
}

.subject-tabs {
  width: 80px;
  background: #f8f8f8;
  border-right: 1px solid #eee;
  overflow-y: auto;
}

.subject-tab {
  padding: 14px 8px;
  text-align: center;
  cursor: pointer;
  border-bottom: 1px solid #eee;
  transition: all 0.3s;
}

.subject-tab.active {
  background: #fff;
  border-left: 3px solid #ff6b6b;
}

.subject-tab .subject-name {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.subject-tab.active .subject-name {
  color: #ff6b6b;
  font-weight: bold;
}

.units-container {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.units-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.unit-link {
  color: #1890ff;
  font-size: 14px;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 6px;
  border: 1px solid #e8e8e8;
  background: #fff;
  transition: all 0.3s;
}

.unit-link:hover {
  background: #e6f7ff;
  border-color: #1890ff;
}

.unit-link:active {
  background: #d6e4fc;
}

.unit-downloaded {
  background: #f5f5f5;
  color: #999;
  cursor: not-allowed;
  border-color: #e8e8e8;
}

.unit-downloaded:hover {
  background: #f5f5f5;
  border-color: #e8e8e8;
}

.empty-text {
  color: #999;
  font-size: 14px;
  text-align: center;
  padding: 40px 20px;
}

.grade-selector {
  padding: 20px;
}

.selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

.selector-body {
  max-height: 400px;
  overflow-y: auto;
}

.selector-section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 14px;
  color: #666;
  margin-bottom: 12px;
  font-weight: 500;
}

.grade-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.grade-item {
  padding: 8px 16px;
  background: #f5f5f5;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.grade-item.active {
  background: #ff6b6b;
  color: #fff;
}

.semester-list {
  display: flex;
  gap: 10px;
}

.semester-item {
  flex: 1;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 6px;
  font-size: 14px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.semester-item.active {
  background: #ff6b6b;
  color: #fff;
}

.selector-footer {
  margin-top: 20px;
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
  max-width: 1200px;
  max-height: 85vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-body {
  padding: 16px;
  overflow-y: auto;
  flex: 1;
  background: #f0f0f0;
}

.modal-body :deep(.docx-preview-wrapper) {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  margin: 0 auto;
  width: 100% !important;
  max-width: 100% !important;
}

.modal-body :deep(.docx-wrapper) {
  background: transparent;
  width: 100% !important;
}

.modal-body :deep(section.docx) {
  box-shadow: none;
  margin-bottom: 20px;
  width: 100% !important;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.btn-close {
  background: #f5f5f5;
  color: #666;
  border: 1px solid #ddd;
  padding: 10px 20px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  flex: 1;
}

.btn-close:hover {
  background: #e8e8e8;
}

.btn-primary {
  background: linear-gradient(135deg, #ff6b6b 0%, #ff8e8e 100%);
  color: #fff;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  flex: 1;
}

.btn-primary:hover {
  opacity: 0.9;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.unit-qcount {
  display: inline-block;
  margin-left: 6px;
  font-size: 12px;
  color: #4facfe;
  background: #e6f7ff;
  padding: 2px 6px;
  border-radius: 4px;
}

.points-cost {
  font-size: 13px;
  color: #ff6b6b;
  font-weight: bold;
}

.paper-config-modal {
  max-width: 500px;
}

.paper-config-body {
  background: #fff;
  padding: 24px;
}

.modal-header {
  padding: 16px 24px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 16px;
  font-weight: bold;
}

.config-item {
  margin-bottom: 24px;
}

.config-item label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 12px;
}

.qty-selector {
  display: flex;
  align-items: center;
  gap: 12px;
}

.qty-btn {
  width: 36px;
  height: 36px;
  border: 1px solid #ddd;
  background: #f5f5f5;
  border-radius: 4px;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.qty-btn:hover {
  background: #e8e8e8;
}

.qty-selector input {
  width: 80px;
  height: 36px;
  text-align: center;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.config-hint {
  margin-left: 12px;
  font-size: 12px;
  color: #999;
}

.distribution-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.distribution-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.dist-name {
  font-size: 14px;
  color: #333;
  min-width: 60px;
}

.dist-total {
  font-size: 12px;
  color: #999;
}

.distribution-item .qty-selector {
  margin-left: auto;
}
</style>
