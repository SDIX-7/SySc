import request from '@/utils/request'
import type { 
  ImageItem, 
  ControlChartData 
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
