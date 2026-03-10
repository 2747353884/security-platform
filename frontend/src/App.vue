<template>
  <div id="app">
    <h1>网络安全态势感知平台</h1>
    <h2>前端开发环境已搭建</h2>
    
    <!-- 显示后端返回的数据 -->
    <div v-if="backendMessage" class="backend-status success">
      ✅ {{ backendMessage }}
    </div>
    <div v-else-if="errorMessage" class="backend-status error">
      ❌ {{ errorMessage }}
    </div>
    <div v-else class="backend-status loading">
      正在连接后端服务...
    </div>
    
    <!-- 测试按钮 -->
    <button @click="testBackend" :disabled="loading">测试后端连接</button>
  </div>
</template>

<script>
// 导入 axios 用于发送 HTTP 请求
import axios from 'axios'

export default {
  name: 'App',
  data() {
    return {
      backendMessage: '',
      errorMessage: '',
      loading: false
    }
  },
  created() {
    // 组件创建时自动测试后端连接
    this.testBackend()
  },
  methods: {
    async testBackend() {
      this.loading = true
      this.errorMessage = ''
      
      try {
        // 调用后端的健康检查接口
        // 注意：这里的 localhost:5000 是后端的地址
        const response = await axios.get('/api/health')
        
        // 请求成功
        this.backendMessage = response.data.message
        console.log('后端连接成功:', response.data)
      } catch (error) {
        // 请求失败
        console.error('后端连接失败:', error)
        this.errorMessage = '无法连接到后端服务，请确保后端服务已启动'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

h1 {
  color: #1890ff;
}

.backend-status {
  margin: 20px auto;
  padding: 15px;
  max-width: 500px;
  border-radius: 4px;
}

.success {
  background-color: #f6ffed;
  border: 1px solid #b7eb8f;
  color: #52c41a;
}

.error {
  background-color: #fff2f0;
  border: 1px solid #ffccc7;
  color: #f5222d;
}

.loading {
  background-color: #e6f7ff;
  border: 1px solid #91d5ff;
  color: #1890ff;
}

button {
  background-color: #1890ff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}

button:hover {
  background-color: #40a9ff;
}

button:disabled {
  background-color: #bfbfbf;
  cursor: not-allowed;
}
</style>