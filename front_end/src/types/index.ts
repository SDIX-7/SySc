export interface ImageItem {
  id: number
  name: string
  hasDefects: boolean
  detection_total_cnts: number
  detection_classes: string[]
  detection_boxes: number[][]
  detection_scores: number[]
  captureTime: string
}

export interface ControlChartData {
  u_list: number[]
  c_list: number[]
  n_list: number[]
  center_line: number
  ucl_list: number[]
  lcl_list: number[]
  abnormal_points: number[]
  abnormal_rules: Record<number, number[]>
  sample_times: string[]
  sample_defects_details: DefectsDetail[]
  statistics: {
    total_samples: number
    total_defects: number
    mean_defects_per_sample: number
    mean_u: number
    total_abnormal_count: number
  }
  message: string
}

export interface DefectsDetail {
  sample_size: number
  total_defects: number
  defects_per_pcb: number[]
  pcb_names: string[]
  capture_times: string[]
}

export interface ApiResponse<T = unknown> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

export interface ProductionLine {
  id: number
  line_code: string
  line_name: string
  line_description?: string
  data_type: string
  model_path?: string
  status: string
  created_at: string
  updated_at?: string
}

export interface ProductionLineCreate {
  line_code: string
  line_name: string
  line_description?: string
  data_type: 'measurement' | 'attribute'
  model_path?: string
  status: 'active' | 'inactive'
}

export interface ProductionLineUpdate {
  line_name?: string
  line_description?: string
  data_type?: 'measurement' | 'attribute'
  model_path?: string
  status?: 'active' | 'inactive'
}

export interface MeasurementData {
  id: number
  line_id: number
  sample_id: string
  measurement_values: number[]
  measurement_time: string
  operator?: string
  equipment?: string
  created_at: string
}

export interface MeasurementDataCreate {
  line_id: number
  sample_id: string
  measurement_values: number[]
  measurement_time?: string
  operator?: string
  equipment?: string
}

export interface AttributeData {
  id: number
  line_id: number
  sample_id: string
  sample_size: number
  defect_count: number
  defect_details: Record<string, any>
  inspection_time: string
  inspector?: string
  created_at: string
}

export interface AttributeDataCreate {
  line_id: number
  sample_id: string
  sample_size: number
  defect_count?: number
  defect_details?: Record<string, any>
  inspection_time?: string
  inspector?: string
}

export interface ControlChartConfig {
  id: number
  line_id: number
  chart_type: string
  control_limit_type: string
  alarm_rules: any[]
  created_at: string
  updated_at?: string
}

export interface SamplingPlan {
  id: number
  line_id?: number
  plan_name: string
  batch_size: number
  aql_value: string
  inspection_level: string
  sample_size?: number
  acceptance_number?: number
  rejection_number?: number
  sampling_type: string
  created_at: string
}

export interface SamplingRecord {
  id: number
  plan_id?: number
  line_id?: number
  batch_id: string
  sample_size: number
  defect_count: number
  judgment?: string
  inspection_status: string
  created_at: string
}

export interface CapabilityIndex {
  value: number
  rating: string
  rating_class: string
  color: string
}

export interface CapabilityIndices {
  cp: CapabilityIndex
  cpk: CapabilityIndex
  pp: CapabilityIndex
  ppk: CapabilityIndex
  cm: CapabilityIndex | null
  cmk: CapabilityIndex | null
}

export interface CapabilityAnalysis {
  id: number
  line_id: number
  analysis_name?: string
  usl: string
  lsl: string
  target?: string
  cp?: string
  cpk?: string
  pp?: string
  ppk?: string
  cm?: string
  cmk?: string
  mean?: string
  sigma_within?: string
  sigma_overall?: string
  sigma_machine?: string
  sample_count: number
  subgroup_count: number
  data_values: number[]
  status: string
  analysis_type: string
  analysis_time: string
  created_at: string
}

export interface CapabilityAnalysisCreate {
  line_id: number
  analysis_name?: string
  usl: number
  lsl: number
  target?: number
  sigma_machine?: number
  data_values: number[]
  analysis_type?: 'process' | 'machine' | 'preliminary'
}

export interface CapabilityAnalysisResult extends CapabilityAnalysis {
  indices: CapabilityIndices
  data_statistics: {
    total_samples: number
    subgroup_count: number
    min_value: number
    max_value: number
    range: number
  }
  normality_test?: {
    is_normal: boolean
    p_value: number
    statistic: number
    test_name: string
  }
  histogram_data?: {
    bins: number[]
    frequencies: number[]
    normal_curve_x: number[]
    normal_curve_y: number[]
  }
}

export interface CapabilityValidation {
  valid: boolean
  warnings: string[]
  data_in_spec: number
  data_out_spec: number
  percent_in_spec: number
}
