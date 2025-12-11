import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import axios from 'axios'

import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'

import {VUE_SOCKET_IO} from './util/socket'

// 导入API模块
import * as api from './api/api'

import './static/css/common.css'
Vue.use(ElementUI)
Vue.use(VUE_SOCKET_IO)

// 将API挂载到Vue原型上
Vue.prototype.$api = api

// 模拟登录数据
const mockUsers = [
  { id: 'admin', password: 'admin123', name: '管理员', role: 'admin' },
  { id: 'detector1', password: 'detector123', name: '检测员1', role: 'detector' },
  { id: 'monitor1', password: 'monitor123', name: '监测员1', role: 'monitor' }
]

// 添加模拟登录拦截器
axios.interceptors.request.use(config => {
  // 如果是登录请求，使用模拟数据
  if (config.url === '/login' && config.method === 'post') {
    return new Promise((resolve, reject) => {
      const { username, password } = config.data
      const user = mockUsers.find(u => u.id === username && u.password === password)
      if (user) {
        resolve({
          data: {
            success: true,
            data: {
              id: user.id,
              name: user.name,
              role: user.role
            }
          }
        })
      } else {
        resolve({
          data: {
            success: false,
            message: '用户名或密码错误'
          }
        })
      }
    })
  }
  return config
})

Vue.config.productionTip = false

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
