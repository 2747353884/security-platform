import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import axios from 'axios'

// 配置 axios 基础 URL（使用代理，所以不需要写完整 URL）
axios.defaults.baseURL = '/'

// 添加请求拦截器，可以在请求头中加入 token 等（这里暂时不需要）
// axios.interceptors.request.use(config => { ... })

const app = createApp(App)
app.use(router)
app.use(ElementPlus)
app.mount('#app')