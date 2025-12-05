import request from '../util/request'

export const detectByImg = (data) => request({
  method: 'post',
  url: '/detectByImg',
  responseType: 'blob',
  data
})

export const getImages = (startDate, endDate) => request({
  method: 'get',
  url: '/images',
  params: {
    startDate,
    endDate
  }
})

export const getControlChartData = () => request({
  method: 'get',
  url: '/control-chart-data'
})
