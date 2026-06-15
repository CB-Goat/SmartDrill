<template>
  <div class="page">
    <van-nav-bar title="登录" />
    
    <van-form @submit="onSubmit" style="margin: 16px">
      <van-cell-group inset>
        <van-field v-model="username" name="username" label="用户名" placeholder="请输入用户名" :rules="[{ required: true, message: '请填写用户名' }]" />
        <van-field v-model="password" type="password" name="password" label="密码" placeholder="请输入密码" :rules="[{ required: true, message: '请填写密码' }]" />
      </van-cell-group>
      
      <div style="margin: 16px">
        <van-button round block type="primary" native-type="submit" class="btn-primary">登录</van-button>
        <van-button round block style="margin-top: 12px" to="/register">注册</van-button>
      </div>
    </van-form>
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
  await userStore.login(username.value, password.value)
  showSuccessToast('登录成功')
  router.push('/')
}
</script>