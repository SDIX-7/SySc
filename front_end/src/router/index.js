import Vue from 'vue'
import VueRouter from 'vue-router'
import HomeView from '../views/HomeView'
import Detecting from '../views/Detecting'
import DetectByImg from '../views/DetectByImg'
import History from '../views/History'
import ProcessControl from '../views/ProcessControl'
// 导入新组件
import UserManagement from '../views/UserManagement'
import EmailSettings from '../views/EmailSettings'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/Detecting',
    name: 'Detecting',
    component: Detecting,
    meta: { requiresAuth: true, permission: 'detect' }
  },
  {
    path: '/DetectByImg',
    name: 'DetectByImg',
    component: DetectByImg,
    meta: { requiresAuth: true, permission: 'detect' }
  },
  {
    path: '/History',
    name: 'History',
    component: History,
    meta: { requiresAuth: true, permission: 'history' }
  },
  {
    path: '/ProcessControl',
    name: 'ProcessControl',
    component: ProcessControl,
    meta: { requiresAuth: true, permission: 'process' }
  },
  // 新增路由
  {
    path: '/UserManagement',
    name: 'UserManagement',
    component: UserManagement,
    meta: { requiresAuth: true, permission: 'management' }
  },
  {
    path: '/EmailSettings',
    name: 'EmailSettings',
    component: EmailSettings,
    meta: { requiresAuth: true, permission: 'email' }
  }
]

const router = new VueRouter({
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 获取Vuex实例
  const store = router.app.$store

  // 检查是否需要登录
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 检查是否已登录
    const isLoggedIn = store.getters['user/isLoggedIn']
    if (!isLoggedIn) {
      // 未登录，跳转到登录页
      next('/')
    } else {
      // 已登录，检查权限
      const permission = to.meta.permission
      if (permission) {
        const hasPermission = store.getters['user/hasPermission'](permission)
        if (hasPermission) {
          // 有权限，放行
          next()
        } else {
          // 无权限，提示并跳转
          router.app.$message.error('您没有权限访问该页面')
          next(from.path || '/Detecting')
        }
      } else {
        // 不需要权限，放行
        next()
      }
    }
  } else {
    // 不需要登录，放行
    next()
  }
})

export default router
