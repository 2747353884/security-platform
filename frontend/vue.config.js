// frontend/vue.config.js
const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  // 配置开发服务器
  devServer: {
    port: 8080,           // 前端运行端口
    proxy: {
      // 将以 /api 开头的请求代理到后端
      '/api': {
        target: 'http://127.0.0.1:5000',  // 后端地址
        changeOrigin: true,
        // 如果后端没有 /api 前缀，可以去掉
        // pathRewrite: { '^/api': '' }
      }
    }
  }
})