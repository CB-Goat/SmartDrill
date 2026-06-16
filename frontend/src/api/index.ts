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

const adminRequest = axios.create({
  baseURL: '/api',
  timeout: 10000
})

adminRequest.interceptors.request.use(config => {
  const adminToken = localStorage.getItem('admin_token')
  if (adminToken) {
    config.headers.Authorization = `Bearer ${adminToken}`
  }
  return config
})

adminRequest.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_user')
      window.location.href = '/admin/login'
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
    getUsers: () => adminRequest.get('/admin/users'),
    updateUser: (id: number, data: any) => adminRequest.put(`/admin/users/${id}`, data),
    getRecharges: () => adminRequest.get('/admin/recharges'),
    getOrders: () => adminRequest.get('/admin/orders'),
    
    getVersions: () => adminRequest.get('/admin/versions'),
    saveVersion: (data: any) => adminRequest.post('/admin/versions', data),
    getGrades: (versionId?: number) => adminRequest.get('/admin/grades', { params: { version_id: versionId } }),
    saveGrade: (data: any) => adminRequest.post('/admin/grades', data),
    getSubjects: (gradeId?: number) => adminRequest.get('/admin/subjects', { params: { grade_id: gradeId } }),
    saveSubject: (data: any) => adminRequest.post('/admin/subjects', data),
    getSemesters: (subjectId?: number) => adminRequest.get('/admin/semesters', { params: { subject_id: subjectId } }),
    saveSemester: (data: any) => adminRequest.post('/admin/semesters', data),
    getUnits: (semesterId?: number) => adminRequest.get('/admin/units', { params: { semester_id: semesterId } }),
    saveUnit: (data: any) => adminRequest.post('/admin/units', data),
    
    getKnowledge: (unitId?: number) => adminRequest.get('/admin/knowledge', { params: { unit_id: unitId } }),
    saveKnowledge: (data: any) => adminRequest.post('/admin/knowledge', data),
    getExamPoints: (knowledgePointId?: number) => adminRequest.get('/admin/exam-points', { params: { knowledge_point_id: knowledgePointId } }),
    saveExamPoint: (data: any) => adminRequest.post('/admin/exam-points', data),
    
    getKnowledgeExamPoints: (unitId?: number) => adminRequest.get('/admin/knowledge-exam-points', { params: { unit_id: unitId } }),
    saveKnowledgeExamPoint: (data: any) => adminRequest.post('/admin/knowledge-exam-points', data),
    
    getQuestionTypes: () => adminRequest.get('/admin/question-types'),
    getDifficulties: () => adminRequest.get('/admin/difficulties'),
    getQuestions: (unitId?: number) => adminRequest.get('/admin/questions', { params: { unit_id: unitId } }),
    saveQuestion: (data: any) => adminRequest.post('/admin/questions', data)
  }
}