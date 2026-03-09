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
  {
    path: '/control-plans',
    name: 'ControlPlanList',
    component: () => import('@/views/ControlPlanList.vue'),
  },
  {
    path: '/control-plans/new',
    name: 'NewControlPlan',
    component: () => import('@/views/ControlPlanForm.vue'),
  },
  {
    path: '/control-plans/:planId',
    name: 'ControlPlanDetail',
    component: () => import('@/views/ControlPlanDetail.vue'),
  },
  {
    path: '/control-plans/:planId/edit',
    name: 'EditControlPlan',
    component: () => import('@/views/ControlPlanForm.vue'),
  },
  {
    path: '/production-lines/:lineId/control-plans',
    name: 'LineControlPlans',
    component: () => import('@/views/ControlPlanList.vue'),
  },
  {
    path: '/production-lines/:lineId/ocaps',
    name: 'LineOCAPs',
    component: () => import('@/views/OCAPList.vue'),
  },
  {
    path: '/ocaps',
    name: 'OCAPList',
    component: () => import('@/views/OCAPList.vue'),
  },
  {
    path: '/ocaps/new',
    name: 'NewOCAP',
    component: () => import('@/views/OCAPForm.vue'),
  },
  {
    path: '/ocaps/:ocapId',
    name: 'OCAPDetail',
    component: () => import('@/views/OCAPDetail.vue'),
  },
  {
    path: '/ocaps/:ocapId/edit',
    name: 'EditOCAP',
    component: () => import('@/views/OCAPForm.vue'),
  },
  {
    path: '/control-chart-configs/:configId/ocaps',
    name: 'ConfigOCAPs',
    component: () => import('@/views/OCAPList.vue'),
  },
  {
    path: '/msa-studies',
    name: 'MSAStudyList',
    component: () => import('@/views/MSAStudyList.vue'),
  },
  {
    path: '/msa-studies/new',
    name: 'NewMSAStudy',
    component: () => import('@/views/MSAStudyForm.vue'),
  },
  {
    path: '/msa-studies/:studyId',
    name: 'MSAStudyDetail',
    component: () => import('@/views/MSAStudyDetail.vue'),
  },
  {
    path: '/msa-studies/:studyId/edit',
    name: 'EditMSAStudy',
    component: () => import('@/views/MSAStudyForm.vue'),
  },
  {
    path: '/production-lines/:lineId/msa-studies',
    name: 'LineMSAStudies',
    component: () => import('@/views/MSAStudyList.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
