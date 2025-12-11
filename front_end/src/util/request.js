import axios from 'axios'
import store from '../store'

// 创建 axios 实例
const request = axios.create({
  // API 请求的默认前缀
  baseURL: process.env.BASE_URL
  // timeout: 5000 // 请求超时时间
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    let cancel
    // 设置cancelToken对象
    config.cancelToken = new axios.CancelToken(c => {
      cancel = c
    })
    // 移除重复请求拦截逻辑，因为它会阻止正常的刷新按钮点击
    store.dispatch('setCancelAxios', cancel)
    store.dispatch('setReqUrl', config.url)
    return config
  }, err => Promise.reject(err)
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    // 增加延迟，相同请求不得在短时间内重复发送
    store.dispatch('delReqUrl', false)
    store.dispatch('setCancelAxios', null)
    return response
  }, err => Promise.reject(err)
)

export default request
