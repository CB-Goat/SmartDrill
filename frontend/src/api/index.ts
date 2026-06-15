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
    
    getVersions: () => request.get('/admin/versions'),
    saveVersion: (data: any) => request.post('/admin/versions', data),
    getGrades: (versionId?: number) => request.get('/admin/grades', { params: { version_id: versionId } }),
    saveGrade: (data: any) => request.post('/admin/grades', data),
    getSubjects: (gradeId?: number) => request.get('/admin/subjects', { params: { grade_id: gradeId } }),
    saveSubject: (data: any) => request.post('/admin/subjects', data),
    getSemesters: (subjectId?: number) => request.get('/admin/semesters', { params: { subject_id: subjectId } }),
    saveSemester: (data: any) => request.post('/admin/semesters', data),
    getUnits: (semesterId?: number) => request.get('/admin/units', { params: { semester_id: semesterId } }),
    saveUnit: (data: any) => request.post('/admin/units', data),
    
    getKnowledge: (unitId?: number) => request.get('/admin/knowledge', { params: { unit_id: unitId } }),
    saveKnowledge: (data: any) => request.post('/admin/knowledge', data),
    getExamPoints: (knowledgePointId?: number) => request.get('/admin/exam-points', { params: { knowledge_point_id: knowledgePointId } }),
    saveExamPoint: (data: any) => request.post('/admin/exam-points', data),
    
    getQuestionTypes: () => request.get('/admin/question-types'),
    getDifficulties: () => request.get('/admin/difficulties'),
    getQuestions: (unitId?: number) => request.get('/admin/questions', { params: { unit_id: unitId } }),
    saveQuestion: (data: any) => request.post('/admin/questions', data)
  }
}