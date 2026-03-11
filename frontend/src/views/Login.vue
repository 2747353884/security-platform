<template>
  <div class="login">
    <h2>用户登录</h2>
    <form @submit.prevent="handleLogin">
      <div>
        <label>用户名：</label>
        <input v-model="username" type="text" required />
      </div>
      <div>
        <label>密码：</label>
        <input v-model="password" type="password" required />
      </div>
      <div>
        <label>
          <input v-model="remember" type="checkbox" /> 记住我
        </label>
      </div>
      <button type="submit" :disabled="loading">登录</button>
    </form>
    <p v-if="error" class="error">{{ error }}</p>
    <p>还没有账号？ <router-link to="/register">立即注册</router-link></p>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  data() {
    return {
      username: '',
      password: '',
      remember: false,
      loading: false,
      error: ''
    }
  },
  methods: {
    async handleLogin() {
      this.loading = true
      this.error = ''
      try {
        const response = await axios.post('/api/login', {
          username: this.username,
          password: this.password,
          remember: this.remember
        })
        if (response.data.code === 200) {
          // 保存用户信息到 localStorage
          localStorage.setItem('user', JSON.stringify(response.data.data))
          // 跳转到首页
          this.$router.push('/')
        } else {
          this.error = response.data.msg
        }
      } catch (err) {
        this.error = err.response?.data?.msg || '登录失败，请稍后重试'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.login { max-width: 400px; margin: 50px auto; padding: 20px; border: 1px solid #ccc; border-radius: 8px; }
div { margin-bottom: 15px; }
label { display: inline-block; width: 80px; }
input { padding: 8px; width: 250px; }
button { padding: 10px 20px; background: #1890ff; color: white; border: none; border-radius: 4px; cursor: pointer; }
button:disabled { background: #ccc; }
.error { color: red; }
</style>