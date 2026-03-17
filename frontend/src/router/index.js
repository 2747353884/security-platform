import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Assets from '../views/Assets.vue'
import AssetDetail from '../views/AssetDetail.vue'
import Vulnerabilities from '../views/Vulnerabilities.vue'
import Scan from '../views/Scan.vue'
// 新增规则与告警页面
import Alerts from '../views/Alerts.vue'
import Rules from '../views/Rules.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/assets', name: 'Assets', component: Assets },
  { path: '/assets/:id', name: 'AssetDetail', component: AssetDetail, props: true },
  { path: '/vulnerabilities', name: 'Vulnerabilities', component: Vulnerabilities },
  { path: '/scan', name: 'Scan', component: Scan },
  // 新增路由
  { path: '/alerts', name: 'Alerts', component: Alerts },
  { path: '/rules', name: 'Rules', component: Rules }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router