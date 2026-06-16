import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/',
    component: () => import('@/views/Home.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/register',
    component: () => import('@/views/Register.vue')
  },
  {
    path: '/recharge',
    component: () => import('@/views/Recharge.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/review',
    component: () => import('@/views/Review.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/practice',
    component: () => import('@/views/Practice.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/orders',
    component: () => import('@/views/Orders.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/login',
    component: () => import('@/views/admin/Login.vue')
  },
  {
    path: '/admin',
    component: () => import('@/views/admin/Layout.vue'),
    meta: { requiresAdmin: true },
    children: [
      { path: '', component: () => import('@/views/admin/Dashboard.vue') },
      { path: 'users', component: () => import('@/views/admin/Users.vue') },
      { path: 'recharges', component: () => import('@/views/admin/Recharges.vue') },
      { path: 'orders', component: () => import('@/views/admin/Orders.vue') },
      { path: 'versions', component: () => import('@/views/admin/Versions.vue') },
      { path: 'grades', component: () => import('@/views/admin/Grades.vue') },
      { path: 'subjects', component: () => import('@/views/admin/Subjects.vue') },
      { path: 'semesters', component: () => import('@/views/admin/Semesters.vue') },
      { path: 'units', component: () => import('@/views/admin/Units.vue') },
      { path: 'knowledge-exam-points', component: () => import('@/views/admin/KnowledgeExamPoints.vue') },
      { path: 'questions', component: () => import('@/views/admin/Questions.vue') }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  if (to.meta.requiresAdmin) {
    const adminToken = localStorage.getItem('admin_token')
    if (!adminToken) {
      next('/admin/login')
      return
    }
  }
  
  if (to.meta.requiresAuth) {
    const userStore = useUserStore()
    
    if (userStore.token && !userStore.userInfo) {
      await userStore.fetchUserInfo()
    }
    
    if (!userStore.isLoggedIn) {
      next('/login')
      return
    }
  }
  
  next()
})

export default router