<template>
  <div class="login-page">
    <div class="login-header">
      <div class="logo">智练通</div>
      <div class="slogan">让学习更高效</div>
    </div>
    
    <div class="login-form">
      <div class="form-title">欢迎登录</div>
      
      <div class="input-group">
        <div class="input-icon">👤</div>
        <input v-model="username" type="text" placeholder="请输入用户名" class="input-field" />
      </div>
      
      <div class="input-group">
        <div class="input-icon">🔒</div>
        <input v-model="password" type="password" placeholder="请输入密码" class="input-field" />
      </div>
      
      <button @click="onSubmit" class="login-btn">登录</button>
      
      <div class="register-link">
        还没有账号？<router-link to="/register">立即注册</router-link>
      </div>
    </div>
    
    <div class="login-footer">
      <div class="tips">💡 首次使用请先注册账号</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { showSuccessToast } from 'vant'

const router = useRouter()
const userStore = useUserStore()
const username = ref('')
const password = ref('')

async function onSubmit() {
  if (!username.value || !password.value) {
    return
  }
  await userStore.login(username.value, password.value)
  showSuccessToast('登录成功')
  router.push('/')
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #ff6b6b 0%, #ff8e8e 50%, #ffa5a5 100%);
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

.logo {
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 8px;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
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
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
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
  border-color: #ff6b6b;
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
  background: linear-gradient(135deg, #ff6b6b 0%, #ff8e8e 100%);
  color: #fff;
  border: none;
  border-radius: 25px;
  font-size: 18px;
  font-weight: bold;
  margin-top: 24px;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
}

.login-btn:active {
  transform: scale(0.98);
}

.register-link {
  text-align: center;
  margin-top: 20px;
  color: #999;
  font-size: 14px;
}

.register-link a {
  color: #ff6b6b;
  text-decoration: none;
  font-weight: bold;
}

.login-footer {
  margin-top: 40px;
  text-align: center;
}

.tips {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
}
</style>