// user.js - Vuex user module

const state = {
  // 用户信息
  userInfo: JSON.parse(localStorage.getItem('userInfo')) || null,
  // 权限列表
  permissions: []
}

const mutations = {
  // 设置用户信息
  SET_USER_INFO (state, userInfo) {
    state.userInfo = userInfo
    localStorage.setItem('userInfo', JSON.stringify(userInfo))
    // 根据角色设置权限
    this.commit('user/SET_PERMISSIONS', userInfo.role)
  },
  // 设置权限
  SET_PERMISSIONS (state, role) {
    switch (role) {
      case 'admin':
        state.permissions = ['detect', 'history', 'process', 'email', 'management']
        break
      case 'monitor':
        state.permissions = ['detect', 'history', 'process', 'email']
        break
      case 'detector':
        state.permissions = ['detect']
        break
      default:
        state.permissions = []
    }
  },
  // 清除用户信息
  CLEAR_USER_INFO (state) {
    state.userInfo = null
    state.permissions = []
    localStorage.removeItem('userInfo')
  }
}

const actions = {
  // 登录
  login ({ commit }, userInfo) {
    return new Promise((resolve, reject) => {
      // 实际项目中这里应该调用API
      // 模拟登录成功
      commit('SET_USER_INFO', userInfo)
      resolve()
    })
  },
  // 登出
  logout ({ commit }) {
    return new Promise((resolve) => {
      commit('CLEAR_USER_INFO')
      resolve()
    })
  }
}

const getters = {
  // 获取用户信息
  getUserInfo: state => state.userInfo,
  // 获取用户角色
  getUserRole: state => state.userInfo ? state.userInfo.role : '',
  // 检查是否有权限
  hasPermission: state => permission => {
    return state.permissions.includes(permission)
  },
  // 检查是否登录
  isLoggedIn: state => !!state.userInfo
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
