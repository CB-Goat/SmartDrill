import axios from 'axios'
import { useUserStore } from '@/stores/user'
import { showToast } from 'vant'

const request = axios.create({
  baseURL: '/api',
  timeout: 10000
})

request.interceptors.request.use(config => {
  const userStore = useUserStore()
  if (userStore.token) {
    config.headers.Authorization = `Bearer ${userStore.token}`
  }
  return config
})

request.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response?.status === 401) {
      const userStore = useUserStore()
      userStore.logout()
      window.location.href = '/login'
    } else {
      showToast(error.response?.data?.message || '请求失败')
    }
    return Promise.reject(error)
  }
)

export const api = {
  login: (username: string, password: string) =>
    request.post('/auth/login', { username, password }),
  
  register: (data: any) =>
    request.post('/auth/register', data),
  
  getUserInfo: () =>
    request.get('/user/info'),
  
  recharge: (amount: number) =>
    request.post('/user/recharge', { amount }),
  
  getSubjects: () =>
    request.get('/subjects'),
  
  getSemesters: (subjectId: number) =>
    request.get(`/subjects/${subjectId}/semesters`),
  
  getUnits: (subjectId: number, semesterId: number) =>
    request.get(`/subjects/${subjectId}/semesters/${semesterId}/units`),
  
  getReviewMaterials: (data: any) =>
    request.post('/materials/review', data),
  
  getPracticeQuestions: (data: any) =>
    request.post('/materials/practice', data),
  
  getOrders: () =>
    request.get('/orders'),
  
  downloadOrder: (orderId: number) =>
    request.get(`/orders/${orderId}/download`, { responseType: 'blob' }),
  
  admin: {
    getUsers: () => request.get('/admin/users'),
    updateUser: (id: number, data: any) => request.put(`/admin/users/${id}`, data),
    getRecharges: () => request.get('/admin/recharges'),
    getOrders: () => request.get('/admin/orders'),
    getKnowledge: () => request.get('/admin/knowledge'),
    saveKnowledge: (data: any) => request.post('/admin/knowledge', data),
    getQuestions: () => request.get('/admin/questions'),
    saveQuestion: (data: any) => request.post('/admin/questions', data)
  }
}