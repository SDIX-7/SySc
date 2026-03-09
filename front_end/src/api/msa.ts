import request from '@/utils/request'

export interface MSAPart {
  id?: number
  msa_study_id?: number
  part_number: string
  part_name?: string
  reference_value?: string
  sort_order?: number
}

export interface MSAOperator {
  id?: number
  msa_study_id?: number
  operator_name: string
  operator_id?: string
  sort_order?: number
}

export interface MSAMeasurement {
  id?: number
  msa_study_id?: number
  part_id: number
  operator_id: number
  replicate: number
  measurement_value: string
  measurement_order?: number
  measured_at?: string
}

export interface MSAResult {
  id?: number
  msa_study_id?: number
  study_type: string
  calculation_method: string
  variance_repeatability?: string
  variance_reproducibility?: string
  variance_grr?: string
  variance_part?: string
  variance_total?: string
  stddev_repeatability?: string
  stddev_reproducibility?: string
  stddev_grr?: string
  stddev_part?: string
  stddev_total?: string
  percent_grr?: string
  percent_tolerance?: string
  ndc?: string
  grr_acceptance?: string
  ndc_acceptance?: string
  overall_acceptance?: string
  detailed_results?: any
  calculated_at?: string
  created_at?: string
}

export interface MSAStudy {
  id?: number
  line_id?: number
  study_name: string
  study_type: string
  status: string
  measurement_system?: string
  characteristic?: string
  specification_lower?: string
  specification_upper?: string
  specification_target?: string
  tolerance?: string
  number_of_parts: number
  number_of_operators: number
  number_of_replicates: number
  random_order: boolean
  created_by?: string
  created_at?: string
  updated_at?: string
  parts?: MSAPart[]
  operators?: MSAOperator[]
  measurements?: MSAMeasurement[]
  result?: MSAResult
}

export interface MSAStudyCreate {
  line_id?: number
  study_name: string
  study_type?: string
  status?: string
  measurement_system?: string
  characteristic?: string
  specification_lower?: string
  specification_upper?: string
  specification_target?: string
  tolerance?: string
  number_of_parts?: number
  number_of_operators?: number
  number_of_replicates?: number
  random_order?: boolean
  created_by?: string
  parts?: MSAPart[]
  operators?: MSAOperator[]
  measurements?: MSAMeasurement[]
}

export function getMSAStudies(params?: {
  line_id?: number
  study_type?: string
  status?: string
}) {
  return request({
    url: '/api/msa-studies',
    method: 'get',
    params
  })
}

export function getMSAStudy(studyId: number) {
  return request({
    url: `/api/msa-studies/${studyId}`,
    method: 'get'
  })
}

export function createMSAStudy(data: MSAStudyCreate) {
  return request({
    url: '/api/msa-studies',
    method: 'post',
    data
  })
}

export function updateMSAStudy(studyId: number, data: any) {
  return request({
    url: `/api/msa-studies/${studyId}`,
    method: 'put',
    data
  })
}

export function deleteMSAStudy(studyId: number) {
  return request({
    url: `/api/msa-studies/${studyId}`,
    method: 'delete'
  })
}

export function getLineMSAStudies(lineId: number) {
  return request({
    url: `/api/production-lines/${lineId}/msa-studies`,
    method: 'get'
  })
}

export function getMSAParts(studyId: number) {
  return request({
    url: `/api/msa-studies/${studyId}/parts`,
    method: 'get'
  })
}

export function createMSAPart(studyId: number, data: MSAPart) {
  return request({
    url: `/api/msa-studies/${studyId}/parts`,
    method: 'post',
    data
  })
}

export function updateMSAPart(studyId: number, partId: number, data: MSAPart) {
  return request({
    url: `/api/msa-studies/${studyId}/parts/${partId}`,
    method: 'put',
    data
  })
}

export function deleteMSAPart(studyId: number, partId: number) {
  return request({
    url: `/api/msa-studies/${studyId}/parts/${partId}`,
    method: 'delete'
  })
}

export function getMSAOperators(studyId: number) {
  return request({
    url: `/api/msa-studies/${studyId}/operators`,
    method: 'get'
  })
}

export function createMSAOperator(studyId: number, data: MSAOperator) {
  return request({
    url: `/api/msa-studies/${studyId}/operators`,
    method: 'post',
    data
  })
}

export function updateMSAOperator(studyId: number, operatorId: number, data: MSAOperator) {
  return request({
    url: `/api/msa-studies/${studyId}/operators/${operatorId}`,
    method: 'put',
    data
  })
}

export function deleteMSAOperator(studyId: number, operatorId: number) {
  return request({
    url: `/api/msa-studies/${studyId}/operators/${operatorId}`,
    method: 'delete'
  })
}

export function getMSAMeasurements(studyId: number) {
  return request({
    url: `/api/msa-studies/${studyId}/measurements`,
    method: 'get'
  })
}

export function createMSAMeasurement(studyId: number, data: MSAMeasurement) {
  return request({
    url: `/api/msa-studies/${studyId}/measurements`,
    method: 'post',
    data
  })
}

export function updateMSAMeasurement(studyId: number, measId: number, data: MSAMeasurement) {
  return request({
    url: `/api/msa-studies/${studyId}/measurements/${measId}`,
    method: 'put',
    data
  })
}

export function deleteMSAMeasurement(studyId: number, measId: number) {
  return request({
    url: `/api/msa-studies/${studyId}/measurements/${measId}`,
    method: 'delete'
  })
}

export function getMSAResult(studyId: number) {
  return request({
    url: `/api/msa-studies/${studyId}/result`,
    method: 'get'
  })
}

export function calculateMSA(studyId: number) {
  return request({
    url: `/api/msa-studies/${studyId}/calculate`,
    method: 'post'
  })
}
