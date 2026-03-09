import request from '@/utils/request'
import type {
  OCAP,
  OCAPCreate,
  OCAPUpdate,
  OCAPSignal,
  OCAPSignalCreate,
  OCAPStep,
  OCAPStepCreate,
  OCAPStepUpdate,
  OCAPExecution,
  OCAPExecutionCreate,
  OCAPExecutionUpdate,
  OCAPRootCause,
  OCAPRootCauseCreate,
  OCAPRootCauseUpdate,
  OCAPCorrectiveAction,
  OCAPCorrectiveActionCreate,
  OCAPCorrectiveActionUpdate
} from '@/types'

export const getOCAPs = (configId?: number, lineId?: number, status?: string, priority?: string) => request<OCAP[]>({
  method: 'get',
  url: '/api/ocaps',
  params: {
    ...(configId ? { control_chart_config_id: configId } : {}),
    ...(lineId ? { line_id: lineId } : {}),
    ...(status ? { status } : {}),
    ...(priority ? { priority } : {})
  }
})

export const getOCAP = (ocapId: number) => request<OCAP>({
  method: 'get',
  url: `/api/ocaps/${ocapId}`
})

export const createOCAP = (data: OCAPCreate) => request<OCAP>({
  method: 'post',
  url: '/api/ocaps',
  data
})

export const updateOCAP = (ocapId: number, data: OCAPUpdate) => request<OCAP>({
  method: 'put',
  url: `/api/ocaps/${ocapId}`,
  data
})

export const deleteOCAP = (ocapId: number) => request({
  method: 'delete',
  url: `/api/ocaps/${ocapId}`
})

export const getConfigOCAPs = (configId: number) => request<OCAP[]>({
  method: 'get',
  url: `/api/control-chart-configs/${configId}/ocaps`
})

export const getOCAPSignals = (ocapId: number) => request<OCAPSignal[]>({
  method: 'get',
  url: `/api/ocaps/${ocapId}/signals`
})

export const addOCAPSignal = (ocapId: number, data: OCAPSignalCreate) => request<OCAPSignal>({
  method: 'post',
  url: `/api/ocaps/${ocapId}/signals`,
  data
})

export const deleteOCAPSignal = (ocapId: number, signalId: number) => request({
  method: 'delete',
  url: `/api/ocaps/${ocapId}/signals/${signalId}`
})

export const getOCAPSteps = (ocapId: number) => request<OCAPStep[]>({
  method: 'get',
  url: `/api/ocaps/${ocapId}/steps`
})

export const addOCAPStep = (ocapId: number, data: OCAPStepCreate) => request<OCAPStep>({
  method: 'post',
  url: `/api/ocaps/${ocapId}/steps`,
  data
})

export const updateOCAPStep = (ocapId: number, stepId: number, data: OCAPStepUpdate) => request<OCAPStep>({
  method: 'put',
  url: `/api/ocaps/${ocapId}/steps/${stepId}`,
  data
})

export const deleteOCAPStep = (ocapId: number, stepId: number) => request({
  method: 'delete',
  url: `/api/ocaps/${ocapId}/steps/${stepId}`
})

export const getOCAPExecutions = (ocapId: number) => request<OCAPExecution[]>({
  method: 'get',
  url: `/api/ocaps/${ocapId}/executions`
})

export const addOCAPExecution = (ocapId: number, data: OCAPExecutionCreate) => request<OCAPExecution>({
  method: 'post',
  url: `/api/ocaps/${ocapId}/executions`,
  data
})

export const updateOCAPExecution = (ocapId: number, execId: number, data: OCAPExecutionUpdate) => request<OCAPExecution>({
  method: 'put',
  url: `/api/ocaps/${ocapId}/executions/${execId}`,
  data
})

export const deleteOCAPExecution = (ocapId: number, execId: number) => request({
  method: 'delete',
  url: `/api/ocaps/${ocapId}/executions/${execId}`
})

export const getOCAPRootCauses = (ocapId: number) => request<OCAPRootCause[]>({
  method: 'get',
  url: `/api/ocaps/${ocapId}/root-causes`
})

export const addOCAPRootCause = (ocapId: number, data: OCAPRootCauseCreate) => request<OCAPRootCause>({
  method: 'post',
  url: `/api/ocaps/${ocapId}/root-causes`,
  data
})

export const updateOCAPRootCause = (ocapId: number, rcId: number, data: OCAPRootCauseUpdate) => request<OCAPRootCause>({
  method: 'put',
  url: `/api/ocaps/${ocapId}/root-causes/${rcId}`,
  data
})

export const deleteOCAPRootCause = (ocapId: number, rcId: number) => request({
  method: 'delete',
  url: `/api/ocaps/${ocapId}/root-causes/${rcId}`
})

export const getOCAPCorrectiveActions = (ocapId: number) => request<OCAPCorrectiveAction[]>({
  method: 'get',
  url: `/api/ocaps/${ocapId}/corrective-actions`
})

export const addOCAPCorrectiveAction = (ocapId: number, data: OCAPCorrectiveActionCreate) => request<OCAPCorrectiveAction>({
  method: 'post',
  url: `/api/ocaps/${ocapId}/corrective-actions`,
  data
})

export const updateOCAPCorrectiveAction = (ocapId: number, caId: number, data: OCAPCorrectiveActionUpdate) => request<OCAPCorrectiveAction>({
  method: 'put',
  url: `/api/ocaps/${ocapId}/corrective-actions/${caId}`,
  data
})

export const deleteOCAPCorrectiveAction = (ocapId: number, caId: number) => request({
  method: 'delete',
  url: `/api/ocaps/${ocapId}/corrective-actions/${caId}`
})

export const exportOCAPExcel = (ocapId: number) => request({
  method: 'get',
  url: `/api/ocaps/${ocapId}/export/excel`,
  responseType: 'blob'
})

export const exportOCAPPdf = (ocapId: number) => request({
  method: 'get',
  url: `/api/ocaps/${ocapId}/export/pdf`,
  responseType: 'blob'
})
