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
                @click="!isDownloaded(unit) && previewUnit(unit)"
              >
                {{ unit.name }}
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
        <div class="modal-header">
          <h3>{{ previewUnitData?.unit_name }}</h3>
          <div>
            <button class="btn-primary" @click="downloadUnit" style="margin-right: 8px">下载（10积分）</button>
            <button class="close-btn" @click="previewVisible = false">×</button>
          </div>
        </div>
        <div class="modal-body" ref="previewContainer"></div>
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

const currentSubject = computed(() => subjects.value[activeSubject.value] || null)

function isDownloaded(unit: any) {
  return activeType.value === 'review' ? unit.review_downloaded : unit.practice_downloaded
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
          ignoreWidth: false,
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
  background: #f0f0f0;
}

.modal-body :deep(.docx-preview-wrapper) {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  margin: 0 auto;
}

.modal-body :deep(.docx-wrapper) {
  background: transparent;
}

.modal-body :deep(section.docx) {
  box-shadow: none;
  margin-bottom: 20px;
}

.btn-primary {
  background: linear-gradient(135deg, #ff6b6b 0%, #ff8e8e 100%);
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
}

.btn-primary:hover {
  opacity: 0.9;
}
</style>
