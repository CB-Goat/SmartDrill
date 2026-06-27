<template>
  <div class="login-page">
    <div class="login-header">
      <div class="logo-container">
        <img src="/logo_original.jpg" alt="智练通" class="logo-img" />
        <div class="logo-text">智练通</div>
      </div>
      <div class="slogan">管理后台</div>
    </div>
    
    <div class="login-form">
      <div class="form-title">管理员登录</div>
      
      <div class="input-group">
        <div class="input-icon">👤</div>
        <input v-model="username" type="text" placeholder="请输入用户名" class="input-field" />
      </div>
      
      <div class="input-group">
        <div class="input-icon">🔒</div>
        <input v-model="password" type="password" placeholder="请输入密码" class="input-field" />
      </div>
      
      <button @click="onSubmit" class="login-btn">登录</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showSuccessToast } from 'vant'

const router = useRouter()
const username = ref('')
const password = ref('')

async function onSubmit() {
  if (!username.value || !password.value) {
    return
  }
  
  try {
    const res = await fetch('/api/admin/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: username.value, password: password.value })
    })
    
    const data = await res.json()
    
    if (!res.ok) {
      throw new Error(data.detail || '登录失败')
    }
    
    localStorage.setItem('admin_token', data.access_token)
    localStorage.setItem('admin_user', JSON.stringify(data.user))
    showSuccessToast('登录成功')
    router.push('/admin')
  } catch (error: any) {
    showSuccessToast(error.message || '登录失败')
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #001529 0%, #002140 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-header {
  text-align: center;
  color: #fff;
  margin-bottom: 40px;
}

.logo-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.logo-img {
  width: 64px;
  height: 64px;
  border-radius: 16px;
}

.logo-text {
  font-size: 36px;
  font-weight: bold;
}

.slogan {
  font-size: 16px;
  opacity: 0.9;
}

.login-form {
  background: #fff;
  border-radius: 20px;
  padding: 32px 24px;
  width: 100%;
  max-width: 360px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.form-title {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  text-align: center;
  margin-bottom: 32px;
}

.input-group {
  display: flex;
  align-items: center;
  background: #f8f8f8;
  border-radius: 12px;
  padding: 0 16px;
  margin-bottom: 16px;
  border: 2px solid transparent;
  transition: border-color 0.3s, background 0.3s;
}

.input-group:focus-within {
  border-color: #1890ff;
  background: #fff;
}

.input-icon {
  font-size: 20px;
  margin-right: 12px;
}

.input-field {
  flex: 1;
  height: 48px;
  border: none;
  background: transparent;
  font-size: 16px;
  color: #333;
  outline: none;
}

.input-field::placeholder {
  color: #999;
}

.login-btn {
  width: 100%;
  height: 50px;
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  color: #fff;
  border: none;
  border-radius: 25px;
  font-size: 18px;
  font-weight: bold;
  margin-top: 24px;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
  box-shadow: 0 4px 15px rgba(24, 144, 255, 0.4);
}

.login-btn:active {
  transform: scale(0.98);
}
</style>