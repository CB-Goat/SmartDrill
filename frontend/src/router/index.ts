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
    path: '/admin',
    component: () => import('@/views/admin/Layout.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      { path: '', component: () => import('@/views/admin/Dashboard.vue') },
      { path: 'users', component: () => import('@/views/admin/Users.vue') },
      { path: 'recharges', component: () => import('@/views/admin/Recharges.vue') },
      { path: 'orders', component: () => import('@/views/admin/Orders.vue') },
      { path: 'knowledge', component: () => import('@/views/admin/Knowledge.vue') },
      { path: 'questions', component: () => import('@/views/admin/Questions.vue') }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  if (userStore.token && !userStore.userInfo) {
    await userStore.fetchUserInfo()
  }
  
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next('/login')
  } else if (to.meta.requiresAdmin && !userStore.isAdmin) {
    next('/')
  } else {
    next()
  }
})

export default router