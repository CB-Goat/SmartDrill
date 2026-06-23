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
      <div class="card review-card">
        <div class="card-title-vertical">单元复习</div>
        <div class="card-body">
          <div v-for="subject in subjects" :key="subject.subject_id" class="subject-section">
            <div class="subject-name">{{ subject.subject_name }}<{{ subject.grade_name }}{{ getSemesterLabel(subject.units[0]?.semester_name) }}>：</div>
            <div class="units-list">
              <span 
                v-for="unit in subject.units" 
                :key="unit.id" 
                class="unit-link"
                @click="previewUnit(unit, 'review')"
              >
                {{ unit.name }}
              </span>
            </div>
          </div>
          <div v-if="subjects.length === 0" class="empty-text">暂无复习资料</div>
        </div>
      </div>
      
      <div class="card practice-card">
        <div class="card-title-vertical">训练刷题</div>
        <div class="card-body">
          <div v-for="subject in subjects" :key="subject.subject_id" class="subject-section">
            <div class="subject-name">{{ subject.subject_name }}<{{ subject.grade_name }}{{ getSemesterLabel(subject.units[0]?.semester_name) }}>：</div>
            <div class="units-list">
              <span 
                v-for="unit in subject.units" 
                :key="unit.id" 
                class="unit-link"
                @click="previewUnit(unit, 'practice')"
              >
                {{ unit.name }}
              </span>
            </div>
          </div>
          <div v-if="subjects.length === 0" class="empty-text">暂无训练题目</div>
        </div>
      </div>
    </div>
    
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
    
    <van-tabbar v-model="active" active-color="#ff6b6b" inactive-color="#999">
      <van-tabbar-item icon="home-o" to="/">首页</van-tabbar-item>
      <van-tabbar-item icon="description" to="/orders">订单</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/profile">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { showToast } from 'vant'

const userStore = useUserStore()
const active = ref(0)
const subjects = ref<any[]>([])

const previewVisible = ref(false)
const previewUnitData = ref<any>(null)
const previewContainer = ref<HTMLElement | null>(null)

onMounted(async () => {
  await userStore.fetchUserInfo()
  await loadHomeData()
})

function getSemesterLabel(semesterName: string) {
  if (!semesterName) return ''
  if (semesterName.includes('上') || semesterName.includes('一')) return '上册'
  if (semesterName.includes('下') || semesterName.includes('二')) return '下册'
  return semesterName
}

async function loadHomeData() {
  try {
    const response = await fetch('/api/user/home-data', {
      headers: { 'Authorization': 'Bearer ' + userStore.token }
    })
    const result = await response.json()
    subjects.value = result.subjects || []
  } catch (error) {
    console.error('加载数据失败')
  }
}

async function previewUnit(unit: any, type: string) {
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
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  flex: 1;
  display: flex;
}

.card-title-vertical {
  writing-mode: vertical-rl;
  text-orientation: upright;
  background: linear-gradient(135deg, #ff6b6b 0%, #ff8e8e 100%);
  color: #fff;
  padding: 20px 12px;
  font-size: 18px;
  font-weight: bold;
  letter-spacing: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.practice-card .card-title-vertical {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.card-body {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  max-height: 500px;
}

.subject-section {
  margin-bottom: 16px;
}

.subject-name {
  font-size: 15px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.units-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.unit-link {
  color: #1890ff;
  font-size: 14px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.3s;
}

.unit-link:hover {
  background: #e6f7ff;
}

.unit-link:active {
  background: #d6e4fc;
}

.empty-text {
  color: #999;
  font-size: 14px;
  text-align: center;
  padding: 20px;
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
