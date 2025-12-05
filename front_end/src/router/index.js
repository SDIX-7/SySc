import Vue from 'vue'
import VueRouter from 'vue-router'
import HomeView from '../views/HomeView'
import Detecting from '../views/Detecting'
import DetectByImg from '../views/DetectByImg'
import History from '../views/History'
import ProcessControl from '../views/ProcessControl'
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
    component: Detecting
  },
  {
    path: '/DetectByImg',
    name: 'DetectByImg',
    component: DetectByImg
  },
  {
    path: '/History',
    name: 'History',
    component: History
  },
  {
    path: '/ProcessControl',
    name: 'ProcessControl',
    component: ProcessControl
  }

]

const router = new VueRouter({
  routes
})

export default router
