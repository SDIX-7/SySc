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
