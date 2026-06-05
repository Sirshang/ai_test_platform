import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    redirect: '/projects',
  },
  {
    path: '/projects',
    component: () => import('../layouts/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'projects',
        component: () => import('../views/ProjectList.vue'),
      },
      {
        path: ':id',
        name: 'project-detail',
        component: () => import('../views/ProjectDetail.vue'),
      },
      {
        path: ':id/api-cases',
        name: 'api-cases',
        component: () => import('../views/ApiCaseList.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const authStore = useAuthStore()
  if (to.meta.public) {
    if (authStore.isAuthenticated && to.name === 'login') {
      return { name: 'projects' }
    }
    return true
  }
  if (!authStore.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  return true
})

export default router
