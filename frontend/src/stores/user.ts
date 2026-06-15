import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref<any>(null)

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value?.role === 'admin')

  async function login(username: string, password: string) {
    const res = await api.login(username, password)
    token.value = res.access_token
    userInfo.value = res.user
    localStorage.setItem('token', res.access_token)
  }

  async function fetchUserInfo() {
    if (token.value) {
      const res = await api.getUserInfo()
      userInfo.value = res
    }
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    isAdmin,
    login,
    fetchUserInfo,
    logout
  }
})