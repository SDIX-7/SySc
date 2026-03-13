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

// Control Plan Types
export type PlanType = 'prototype' | 'pre-launch' | 'production'
export type ControlPlanStatus = 'draft' | 'approved' | 'active' | 'obsolete'

export interface ControlPlanItem {
  id: number
  control_plan_id: number
  part_process_number?: string
  process_name?: string
  operation_description?: string
  machine_device_jig_tools?: string
  characteristic_no?: string
  product_characteristic?: string
  process_characteristic?: string
  special_characteristic_class?: string
  specification_tolerance?: string
  evaluation_measurement_technique?: string
  sample_size?: string
  sample_frequency?: string
  control_method?: string
  reaction_plan?: string
  sort_order: number
  created_at: string
  updated_at: string
}

export interface ControlPlanItemCreate {
  part_process_number?: string
  process_name?: string
  operation_description?: string
  machine_device_jig_tools?: string
  characteristic_no?: string
  product_characteristic?: string
  process_characteristic?: string
  special_characteristic_class?: string
  specification_tolerance?: string
  evaluation_measurement_technique?: string
  sample_size?: string
  sample_frequency?: string
  control_method?: string
  reaction_plan?: string
  sort_order?: number
}

export interface ControlPlan {
  id: number
  line_id: number
  plan_type: PlanType
  control_plan_number?: string
  part_number?: string
  latest_change_level?: string
  part_name?: string
  part_description?: string
  organization_plant?: string
  organization_code?: string
  key_contact?: string
  key_contact_phone?: string
  core_team?: string
  org_approval_date?: string
  org_approval_by?: string
  other_approval_date?: string
  other_approval_by?: string
  date_orig?: string
  date_rev?: string
  customer_eng_approval_date?: string
  customer_eng_approval_by?: string
  customer_quality_approval_date?: string
  customer_quality_approval_by?: string
  page_number?: number
  total_pages?: number
  version: string
  status: ControlPlanStatus
  created_by?: string
  created_at: string
  updated_at: string
  items?: ControlPlanItem[]
}

export interface ControlPlanCreate {
  line_id: number
  plan_type?: PlanType
  control_plan_number?: string
  part_number?: string
  latest_change_level?: string
  part_name?: string
  part_description?: string
  organization_plant?: string
  organization_code?: string
  key_contact?: string
  key_contact_phone?: string
  core_team?: string
  org_approval_date?: string
  org_approval_by?: string
  other_approval_date?: string
  other_approval_by?: string
  date_orig?: string
  date_rev?: string
  customer_eng_approval_date?: string
  customer_eng_approval_by?: string
  customer_quality_approval_date?: string
  customer_quality_approval_by?: string
  page_number?: number
  total_pages?: number
  version?: string
  status?: ControlPlanStatus
  created_by?: string
  items?: ControlPlanItemCreate[]
}

export interface ControlPlanUpdate {
  plan_type?: PlanType
  control_plan_number?: string
  part_number?: string
  latest_change_level?: string
  part_name?: string
  part_description?: string
  organization_plant?: string
  organization_code?: string
  key_contact?: string
  key_contact_phone?: string
  core_team?: string
  org_approval_date?: string
  org_approval_by?: string
  other_approval_date?: string
  other_approval_by?: string
  date_orig?: string
  date_rev?: string
  customer_eng_approval_date?: string
  customer_eng_approval_by?: string
  customer_quality_approval_date?: string
  customer_quality_approval_by?: string
  page_number?: number
  total_pages?: number
  version?: string
  status?: ControlPlanStatus
}

// OCAP Types
export type SignalType = 'point_beyond_3sigma' | 'run_9' | 'trend_6' | 'zone_2of3' | 'zone_4of5' | 'run_8' | 'run_6' | 'run_14' | 'run_15'
export type OCAPPriority = 'critical' | 'high' | 'medium' | 'low'
export type OCAPStatus = 'draft' | 'active' | 'executing' | 'completed' | 'closed'
export type OCAPPhase = 'containment' | 'investigation' | 'correction' | 'verification'
export type ActionType = 'immediate' | 'short_term' | 'long_term'
export type ExecutionStatus = 'pending' | 'in_progress' | 'completed' | 'skipped' | 'failed'
export type AnalysisMethod = '5whys' | 'fishbone' | 'pareto' | 'fta'
export type CorrectiveActionType = 'temporary' | 'permanent'
export type CorrectiveActionStatus = 'planned' | 'in_progress' | 'completed' | 'verified'
export type ProductDisposition = 'release' | 'rework' | 'scrap' | 'concession'

export interface OCAPSignal {
  id: number
  ocap_id: number
  signal_time?: string
  signal_type?: SignalType
  signal_value?: string
  control_limit_value?: string
  subgroup_index?: number
  raw_data_snapshot?: Record<string, any>
  chart_snapshot_url?: string
  detected_by: string
  created_at: string
}

export interface OCAPSignalCreate {
  signal_time?: string
  signal_type?: SignalType
  signal_value?: string
  control_limit_value?: string
  subgroup_index?: number
  raw_data_snapshot?: Record<string, any>
  chart_snapshot_url?: string
  detected_by?: string
}

export interface OCAPStep {
  id: number
  ocap_id: number
  phase: OCAPPhase
  step_number: number
  action_type: ActionType
  action_description?: string
  responsible_role?: string
  responsible_person?: string
  expected_duration_minutes?: number
  deadline?: string
  is_mandatory: boolean
  prerequisites?: number[]
  sort_order: number
  created_at: string
  updated_at: string
}

export interface OCAPStepCreate {
  phase?: OCAPPhase
  step_number?: number
  action_type?: ActionType
  action_description?: string
  responsible_role?: string
  responsible_person?: string
  expected_duration_minutes?: number
  deadline?: string
  is_mandatory?: boolean
  prerequisites?: number[]
  sort_order?: number
}

export interface OCAPStepUpdate extends OCAPStepCreate {}

export interface OCAPExecution {
  id: number
  ocap_id: number
  step_id?: number
  status: ExecutionStatus
  started_at?: string
  completed_at?: string
  executed_by?: string
  notes?: string
  evidence_urls?: string[]
  containment_action_taken?: string
  product_disposition?: ProductDisposition
  created_at: string
  updated_at: string
}

export interface OCAPExecutionCreate {
  step_id?: number
  status?: ExecutionStatus
  started_at?: string
  completed_at?: string
  executed_by?: string
  notes?: string
  evidence_urls?: string[]
  containment_action_taken?: string
  product_disposition?: ProductDisposition
}

export interface OCAPExecutionUpdate extends OCAPExecutionCreate {}

export interface OCAPRootCause {
  id: number
  ocap_id: number
  analysis_method: AnalysisMethod
  why_1?: string
  why_2?: string
  why_3?: string
  why_4?: string
  why_5?: string
  fishbone_category?: string
  root_cause_description?: string
  contributing_factors?: string[]
  evidence_collected?: Record<string, any>
  verified: boolean
  verified_by?: string
  verified_at?: string
  created_at: string
  updated_at: string
}

export interface OCAPRootCauseCreate {
  analysis_method?: AnalysisMethod
  why_1?: string
  why_2?: string
  why_3?: string
  why_4?: string
  why_5?: string
  fishbone_category?: string
  root_cause_description?: string
  contributing_factors?: string[]
  evidence_collected?: Record<string, any>
  verified?: boolean
  verified_by?: string
  verified_at?: string
}

export interface OCAPRootCauseUpdate extends OCAPRootCauseCreate {}

export interface OCAPCorrectiveAction {
  id: number
  ocap_id: number
  root_cause_id?: number
  action_description?: string
  action_type: CorrectiveActionType
  responsible_person?: string
  target_date?: string
  actual_date?: string
  effectiveness_verified: boolean
  verification_method?: string
  verification_result?: string
  status: CorrectiveActionStatus
  created_at: string
  updated_at: string
}

export interface OCAPCorrectiveActionCreate {
  root_cause_id?: number
  action_description?: string
  action_type?: CorrectiveActionType
  responsible_person?: string
  target_date?: string
  actual_date?: string
  effectiveness_verified?: boolean
  verification_method?: string
  verification_result?: string
  status?: CorrectiveActionStatus
}

export interface OCAPCorrectiveActionUpdate extends OCAPCorrectiveActionCreate {}

export interface OCAP {
  id: number
  control_chart_config_id?: number
  line_id?: number
  name: string
  description?: string
  signal_type?: SignalType
  priority: OCAPPriority
  severity_score: number
  scope_score: number
  trend_score: number
  overall_priority_score: number
  status: OCAPStatus
  is_active: boolean
  created_by?: string
  created_at: string
  updated_at: string
  signals?: OCAPSignal[]
  steps?: OCAPStep[]
  executions?: OCAPExecution[]
  root_causes?: OCAPRootCause[]
  corrective_actions?: OCAPCorrectiveAction[]
}

export interface OCAPCreate {
  control_chart_config_id?: number
  line_id?: number
  name: string
  description?: string
  signal_type?: SignalType
  priority?: OCAPPriority
  severity_score?: number
  scope_score?: number
  trend_score?: number
  overall_priority_score?: number
  status?: OCAPStatus
  is_active?: boolean
  created_by?: string
  signals?: OCAPSignalCreate[]
  steps?: OCAPStepCreate[]
}

export interface OCAPUpdate {
  name?: string
  description?: string
  signal_type?: SignalType
  priority?: OCAPPriority
  severity_score?: number
  scope_score?: number
  trend_score?: number
  overall_priority_score?: number
  status?: OCAPStatus
  is_active?: boolean
}

export type MSAStudyType = 'grr' | 'bias' | 'stability' | 'linearity'
export type MSAStudyStatus = 'draft' | 'in_progress' | 'completed'
export type MSAAcceptance = 'acceptable' | 'conditional' | 'unacceptable'

export interface MSAPart {
  id?: number
  msa_study_id?: number
  part_number: string
  part_name?: string
  reference_value?: number | string
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
  measurement_value: string | number
  measurement_order?: number
  measured_at?: string
}

export interface MSAResult {
  id?: number
  msa_study_id?: number
  study_type: MSAStudyType
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
  grr_acceptance?: MSAAcceptance
  ndc_acceptance?: MSAAcceptance
  overall_acceptance?: MSAAcceptance
  detailed_results?: Record<string, any>
  calculated_at?: string
  created_at?: string
}

export interface MSAStudy {
  id?: number
  line_id?: number
  study_name: string
  study_type: MSAStudyType
  status: MSAStudyStatus
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
  study_type?: MSAStudyType
  status?: MSAStudyStatus
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

export interface MSAStudyUpdate extends Partial<MSAStudyCreate> {}
