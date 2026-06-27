<template>
  <div class="page">
    <van-nav-bar title="注册" left-arrow @click-left="$router.back()" />
    
    <van-form @submit="onSubmit" style="margin: 16px">
      <div class="register-banner">
        🎁 新用户注册即送 100 积分
      </div>
      <van-cell-group inset>
        <van-field v-model="form.username" name="username" label="用户名" placeholder="请输入用户名" :rules="[{ required: true, message: '请填写用户名' }]" />
        <van-field v-model="form.password" type="password" name="password" label="密码" placeholder="请输入密码" :rules="[{ required: true, message: '请填写密码' }]" />
        <van-field v-model="form.confirmPassword" type="password" name="confirmPassword" label="确认密码" placeholder="请再次输入密码" :rules="[{ required: true, message: '请确认密码' }]" />
        <van-field v-model="form.phone" name="phone" label="手机号" placeholder="请输入手机号" :rules="[{ required: true, message: '请填写手机号' }]" />
      </van-cell-group>
      
      <div style="margin: 16px">
        <van-button round block type="primary" native-type="submit" class="btn-primary">注册</van-button>
      </div>
    </van-form>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api'
import { showSuccessToast } from 'vant'

const router = useRouter()
const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  phone: ''
})

async function onSubmit() {
  if (form.password !== form.confirmPassword) {
    return
  }
  await api.register(form)
  showSuccessToast('注册成功，赠送100积分')
  router.push('/login')
}
</script>

<style scoped>
.register-banner {
  text-align: center;
  padding: 16px;
  background: linear-gradient(135deg, #fff5e6 0%, #ffecd2 100%);
  border-radius: 12px;
  font-size: 16px;
  font-weight: bold;
  color: #ff6b35;
  margin-bottom: 16px;
}
</style>