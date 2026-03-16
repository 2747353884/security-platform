import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Assets from '../views/Assets.vue'
import AssetDetail from '../views/AssetDetail.vue'
import Vulnerabilities from '../views/Vulnerabilities.vue'
import Scan from '../views/Scan.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/assets', name: 'Assets', component: Assets },
  { path: '/assets/:id', name: 'AssetDetail', component: AssetDetail, props: true },
  { path: '/vulnerabilities', name: 'Vulnerabilities', component: Vulnerabilities },
  { path: '/scan', name: 'Scan', component: Scan }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router