import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
  },
  {
    path: '/detect-by-img',
    name: 'DetectByImg',
    component: () => import('@/views/DetectByImg.vue'),
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('@/views/History.vue'),
  },
  {
    path: '/process-control',
    name: 'ProcessControl',
    component: () => import('@/views/ProcessControl.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
