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

// 登录相关API
export const login = (data) => {
  // 直接返回模拟登录数据，不发送到后端
  return new Promise((resolve) => {
    // 模拟登录数据
    const mockUsers = [
      { id: 'admin', password: 'admin123', name: '管理员', role: 'admin' },
      { id: 'detector1', password: 'detector123', name: '检测员1', role: 'detector' },
      { id: 'monitor1', password: 'monitor123', name: '监测员1', role: 'monitor' }
    ]

    // 验证用户名和密码
    const { username, password } = data
    const user = mockUsers.find(u => u.id === username && u.password === password)

    if (user) {
      resolve({
        success: true,
        data: {
          id: user.id,
          name: user.name,
          role: user.role
        }
      })
    } else {
      resolve({
        success: false,
        message: '用户名或密码错误'
      })
    }
  })
}

export const logout = () => request({
  method: 'post',
  url: '/logout'
})

// 用户管理API
export const getUserList = () => request({
  method: 'get',
  url: '/users'
})

export const addUser = (data) => request({
  method: 'post',
  url: '/users',
  data
})

export const deleteUser = (id) => request({
  method: 'delete',
  url: `/users/${id}`
})

// 邮箱设置API
export const getEmailSettings = () => request({
  method: 'get',
  url: '/email-settings'
})

export const saveEmailSettings = (data) => request({
  method: 'put',
  url: '/email-settings',
  data
})
