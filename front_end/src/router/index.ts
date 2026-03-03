import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
  },
  {
    path: '/production-lines',
    name: 'ProductionLines',
    component: () => import('@/views/ProductionLines.vue'),
  },
  {
    path: '/production-lines/:id',
    name: 'ProductionLineDashboard',
    component: () => import('@/views/ProductionLineDashboard.vue'),
  },
  {
    path: '/production-lines/:id/data-collection',
    name: 'LineDataCollection',
    component: () => import('@/views/LineDataCollection.vue'),
  },
  {
    path: '/production-lines/:id/history',
    name: 'LineHistory',
    component: () => import('@/views/LineHistory.vue'),
  },
  {
    path: '/production-lines/:id/control-chart',
    name: 'LineControlChart',
    component: () => import('@/views/LineControlChart.vue'),
  },
  {
    path: '/production-lines/:id/capability-analysis',
    name: 'LineCapabilityAnalysis',
    component: () => import('@/views/CapabilityAnalysis.vue'),
  },
  {
    path: '/production-lines/:id/capability-analysis/new',
    name: 'NewCapabilityAnalysis',
    component: () => import('@/views/CapabilityAnalysisForm.vue'),
  },
  {
    path: '/capability-analysis/:analysisId',
    name: 'CapabilityAnalysisDetail',
    component: () => import('@/views/CapabilityAnalysisDetail.vue'),
  },
  {
    path: '/capability-analysis/history',
    name: 'CapabilityAnalysisHistory',
    component: () => import('@/views/CapabilityAnalysisHistory.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
