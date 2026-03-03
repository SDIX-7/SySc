import request from '@/utils/request'
import type { 
  ImageItem, 
  ControlChartData,
  ProductionLine,
  ProductionLineCreate,
  ProductionLineUpdate,
  MeasurementData,
  MeasurementDataCreate,
  AttributeData,
  AttributeDataCreate,
  ControlChartConfig,
  SamplingPlan,
  SamplingRecord,
  CapabilityAnalysis,
  CapabilityAnalysisCreate,
  CapabilityAnalysisResult,
  CapabilityValidation
} from '@/types'

export const detectByImg = (data: FormData) => request({
  method: 'post',
  url: '/api/detectByImg',
  responseType: 'blob',
  data,
  headers: {
    'Content-Type': 'multipart/form-data'
  }
})

export const getImages = (startDate?: string, endDate?: string) => request({
  method: 'get',
  url: '/api/images',
  params: {
    startDate,
    endDate
  }
})

export const getImageById = (id: number) => request<ImageItem>({
  method: 'get',
  url: `/api/images/${id}`
})

export const getControlChartData = () => request<ControlChartData>({
  method: 'get',
  url: '/api/control-chart-data'
})

export const createProductionLine = (data: ProductionLineCreate) => request<ProductionLine>({
  method: 'post',
  url: '/api/production-lines',
  data
})

export const getProductionLines = () => request<ProductionLine[]>({
  method: 'get',
  url: '/api/production-lines'
})

export const getProductionLine = (id: number) => request<ProductionLine>({
  method: 'get',
  url: `/api/production-lines/${id}`
})

export const updateProductionLine = (id: number, data: ProductionLineUpdate) => request<ProductionLine>({
  method: 'put',
  url: `/api/production-lines/${id}`,
  data
})

export const deleteProductionLine = (id: number) => request({
  method: 'delete',
  url: `/api/production-lines/${id}`
})

export interface ModelFile {
  filename: string
  path: string
  size: number
  size_formatted: string
}

export const getModelFiles = () => request<{ files: ModelFile[] }>({
  method: 'get',
  url: '/api/model-files'
})

export const createMeasurementData = (data: MeasurementDataCreate) => request<MeasurementData>({
  method: 'post',
  url: '/api/measurement-data',
  data
})

export const getMeasurementData = (lineId?: number) => request<MeasurementData[]>({
  method: 'get',
  url: '/api/measurement-data',
  params: lineId ? { line_id: lineId } : undefined
})

export const createAttributeData = (data: AttributeDataCreate) => request<AttributeData>({
  method: 'post',
  url: '/api/attribute-data',
  data
})

export const getAttributeData = (lineId?: number) => request<AttributeData[]>({
  method: 'get',
  url: '/api/attribute-data',
  params: lineId ? { line_id: lineId } : undefined
})

export const getControlChartConfigs = (lineId?: number) => request<ControlChartConfig[]>({
  method: 'get',
  url: '/api/control-chart-config',
  params: lineId ? { line_id: lineId } : undefined
})

export const createSamplingPlan = (data: any) => request<SamplingPlan>({
  method: 'post',
  url: '/api/sampling-plans',
  data
})

export const getSamplingPlans = (lineId?: number) => request<SamplingPlan[]>({
  method: 'get',
  url: '/api/sampling-plans',
  params: lineId ? { line_id: lineId } : undefined
})

export const getSamplingPlan = (id: number) => request<SamplingPlan>({
  method: 'get',
  url: `/api/sampling-plans/${id}`
})

export const deleteSamplingPlan = (id: number) => request({
  method: 'delete',
  url: `/api/sampling-plans/${id}`
})

export const createSamplingRecord = (data: any) => request<SamplingRecord>({
  method: 'post',
  url: '/api/sampling-records',
  data
})

export const getSamplingRecords = (planId?: number, lineId?: number) => request<SamplingRecord[]>({
  method: 'get',
  url: '/api/sampling-records',
  params: {
    ...(planId ? { plan_id: planId } : {}),
    ...(lineId ? { line_id: lineId } : {})
  }
})

export const createCapabilityAnalysis = (data: CapabilityAnalysisCreate) => request<CapabilityAnalysisResult>({
  method: 'post',
  url: '/api/capability-analysis',
  data
})

export const getCapabilityAnalyses = (lineId?: number, limit?: number) => request<CapabilityAnalysis[]>({
  method: 'get',
  url: '/api/capability-analysis',
  params: {
    ...(lineId ? { line_id: lineId } : {}),
    ...(limit ? { limit } : {})
  }
})

export const getCapabilityAnalysis = (id: number) => request<CapabilityAnalysisResult>({
  method: 'get',
  url: `/api/capability-analysis/${id}`
})

export const deleteCapabilityAnalysis = (id: number) => request({
  method: 'delete',
  url: `/api/capability-analysis/${id}`
})

export const validateCapabilityLimits = (usl: number, lsl: number, dataValues: number[]) => request<CapabilityValidation>({
  method: 'post',
  url: '/api/capability-analysis/validate',
  data: { usl, lsl, data_values: dataValues }
})

export const normalityTest = (dataValues: number[]) => request<{
  is_normal: boolean
  p_value: number
  statistic: number
  test_name: string
}>({
  method: 'post',
  url: '/api/capability-analysis/normality-test',
  data: dataValues
})
