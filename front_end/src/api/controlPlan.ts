import request from '@/utils/request'
import type {
  ControlPlan,
  ControlPlanCreate,
  ControlPlanUpdate,
  ControlPlanItem,
  ControlPlanItemCreate
} from '@/types'

export const getControlPlans = (lineId?: number, planType?: string, status?: string) => request<ControlPlan[]>({
  method: 'get',
  url: '/api/control-plans',
  params: {
    ...(lineId ? { line_id: lineId } : {}),
    ...(planType ? { plan_type: planType } : {}),
    ...(status ? { status } : {})
  }
})

export const getControlPlan = (planId: number) => request<ControlPlan>({
  method: 'get',
  url: `/api/control-plans/${planId}`
})

export const createControlPlan = (data: ControlPlanCreate) => request<ControlPlan>({
  method: 'post',
  url: '/api/control-plans',
  data
})

export const updateControlPlan = (planId: number, data: ControlPlanUpdate) => request<ControlPlan>({
  method: 'put',
  url: `/api/control-plans/${planId}`,
  data
})

export const deleteControlPlan = (planId: number) => request({
  method: 'delete',
  url: `/api/control-plans/${planId}`
})

export const getLineControlPlans = (lineId: number) => request<ControlPlan[]>({
  method: 'get',
  url: `/api/production-lines/${lineId}/control-plans`
})

export const getControlPlanItems = (planId: number) => request<ControlPlanItem[]>({
  method: 'get',
  url: `/api/control-plans/${planId}/items`
})

export const addControlPlanItem = (planId: number, data: ControlPlanItemCreate) => request<ControlPlanItem>({
  method: 'post',
  url: `/api/control-plans/${planId}/items`,
  data
})

export const updateControlPlanItem = (planId: number, itemId: number, data: ControlPlanItemCreate) => request<ControlPlanItem>({
  method: 'put',
  url: `/api/control-plans/${planId}/items/${itemId}`,
  data
})

export const deleteControlPlanItem = (planId: number, itemId: number) => request({
  method: 'delete',
  url: `/api/control-plans/${planId}/items/${itemId}`
})

export const exportControlPlanExcel = (planId: number) => request({
  method: 'get',
  url: `/api/control-plans/${planId}/export/excel`,
  responseType: 'blob'
})

export const exportControlPlanPdf = (planId: number) => request({
  method: 'get',
  url: `/api/control-plans/${planId}/export/pdf`,
  responseType: 'blob'
})
