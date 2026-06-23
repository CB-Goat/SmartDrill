<template>
  <div class="profile-page">
    <div class="header">
      <h2>我的</h2>
    </div>
    
    <div class="content">
      <van-cell-group inset>
        <van-cell title="用户名" :value="userStore.userInfo?.username" />
        <van-cell title="手机号" :value="userStore.userInfo?.phone || '未设置'" is-link @click="showPhoneDialog = true" />
        <van-cell title="我的积分" :value="userStore.userInfo?.points || 0" />
        <van-cell title="孩子年级" :value="childGradeName || '未设置'" is-link @click="showGradePicker = true" />
      </van-cell-group>
      
      <van-cell-group inset style="margin-top: 16px">
        <van-cell title="充值" is-link to="/recharge" />
        <van-cell title="修改密码" is-link @click="showPasswordDialog = true" />
        <van-cell title="我的订单" is-link to="/orders" />
      </van-cell-group>
      
      <div style="margin-top: 24px; padding: 0 16px">
        <van-button block type="danger" @click="handleLogout">退出登录</van-button>
      </div>
    </div>
    
    <van-dialog v-model:show="showPhoneDialog" title="修改手机号" show-cancel-button @confirm="updatePhone">
      <van-field v-model="newPhone" placeholder="请输入新手机号" type="tel" />
    </van-dialog>
    
    <van-dialog v-model:show="showPasswordDialog" title="修改密码" show-cancel-button @confirm="updatePassword">
      <van-field v-model="oldPassword" placeholder="请输入旧密码" type="password" />
      <van-field v-model="newPassword" placeholder="请输入新密码" type="password" />
    </van-dialog>
    
    <van-popup v-model:show="showGradePicker" position="bottom" round>
      <van-picker
        title="选择孩子年级"
        :columns="gradeColumns"
        @confirm="onGradeConfirm"
        @cancel="showGradePicker = false"
      />
    </van-popup>
    
    <van-tabbar v-model="active" active-color="#ff6b6b" inactive-color="#999">
      <van-tabbar-item icon="home-o" to="/">首页</van-tabbar-item>
      <van-tabbar-item icon="description" to="/orders">订单</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/profile">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { showToast } from 'vant'

const router = useRouter()
const userStore = useUserStore()
const active = ref(2)

const showPhoneDialog = ref(false)
const showPasswordDialog = ref(false)
const showGradePicker = ref(false)

const newPhone = ref('')
const oldPassword = ref('')
const newPassword = ref('')

const grades = ref<any[]>([])
const childGradeName = ref('')

const gradeColumns = computed(() => {
  const versions: any = {}
  grades.value.forEach(g => {
    if (!versions[g.version_name]) {
      versions[g.version_name] = []
    }
    versions[g.version_name].push({ text: g.name, value: g.id })
  })
  
  return Object.entries(versions).map(([version, grades]) => ({
    text: version,
    children: grades
  }))
})

onMounted(async () => {
  await userStore.fetchUserInfo()
  await loadGrades()
  await loadChildGrade()
})

async function loadGrades() {
  try {
    const response = await fetch('/api/subjects/grades', {
      headers: { 'Authorization': 'Bearer ' + userStore.token }
    })
    const data = await response.json()
    grades.value = data
  } catch (error) {
    console.error('加载年级失败')
  }
}

async function loadChildGrade() {
  try {
    const response = await fetch('/api/user/home-data', {
      headers: { 'Authorization': 'Bearer ' + userStore.token }
    })
    const data = await response.json()
    childGradeName.value = data.grade_name || ''
  } catch (error) {
    console.error('加载年级失败')
  }
}

async function updatePhone() {
  if (!newPhone.value) {
    showToast('请输入手机号')
    return
  }
  
  try {
    const response = await fetch('/api/user/update-phone', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + userStore.token,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ phone: newPhone.value })
    })
    
    if (response.ok) {
      showToast('修改成功')
      await userStore.fetchUserInfo()
      newPhone.value = ''
    } else {
      showToast('修改失败')
    }
  } catch (error) {
    showToast('修改失败')
  }
}

async function updatePassword() {
  if (!oldPassword.value || !newPassword.value) {
    showToast('请填写完整')
    return
  }
  
  try {
    const response = await fetch('/api/user/update-password', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + userStore.token,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        old_password: oldPassword.value,
        new_password: newPassword.value
      })
    })
    
    const result = await response.json()
    
    if (response.ok) {
      showToast('修改成功')
      oldPassword.value = ''
      newPassword.value = ''
    } else {
      showToast(result.detail || '修改失败')
    }
  } catch (error) {
    showToast('修改失败')
  }
}

async function onGradeConfirm({ selectedOptions }) {
  const gradeId = selectedOptions[selectedOptions.length - 1].value
  
  try {
    const response = await fetch('/api/user/set-child-grade', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + userStore.token,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ grade_id: gradeId })
    })
    
    const result = await response.json()
    
    if (response.ok) {
      showToast('设置成功')
      childGradeName.value = result.grade_name
      showGradePicker.value = false
    } else {
      showToast(result.detail || '设置失败')
    }
  } catch (error) {
    showToast('设置失败')
  }
}

function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 60px;
}

.header {
  background: linear-gradient(135deg, #ff6b6b 0%, #ff8e8e 100%);
  padding: 40px 20px 20px;
  color: #fff;
}

.header h2 {
  margin: 0;
  font-size: 24px;
}

.content {
  padding: 16px 0;
}
</style>