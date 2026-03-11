<template>
  <div class="register">
    <h2>用户注册</h2>
    <form @submit.prevent="handleRegister">
      <div>
        <label>用户名：</label>
        <input v-model="username" type="text" required />
      </div>
      <div>
        <label>邮箱：</label>
        <input v-model="email" type="email" required />
      </div>
      <div>
        <label>密码：</label>
        <input v-model="password" type="password" required />
      </div>
      <div>
        <label>确认密码：</label>
        <input v-model="confirmPassword" type="password" required />
      </div>
      <button type="submit" :disabled="loading">注册</button>
    </form>
    <p v-if="error" class="error">{{ error }}</p>
    <p>已有账号？ <router-link to="/login">去登录</router-link></p>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  data() {
    return {
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      loading: false,
      error: ''
    }
  },
  methods: {
    async handleRegister() {
      if (this.password !== this.confirmPassword) {
        this.error = '两次输入的密码不一致'
        return
      }
      this.loading = true
      this.error = ''
      try {
        const response = await axios.post('/api/register', {
          username: this.username,
          email: this.email,
          password: this.password
        })
        if (response.data.code === 200) {
          // 注册成功，跳转到登录页
          alert('注册成功，请登录')
          this.$router.push('/login')
        } else {
          this.error = response.data.msg
        }
      } catch (err) {
        this.error = err.response?.data?.msg || '注册失败，请稍后重试'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.register { max-width: 400px; margin: 50px auto; padding: 20px; border: 1px solid #ccc; border-radius: 8px; }
div { margin-bottom: 15px; }
label { display: inline-block; width: 80px; }
input { padding: 8px; width: 250px; }
button { padding: 10px 20px; background: #1890ff; color: white; border: none; border-radius: 4px; cursor: pointer; }
button:disabled { background: #ccc; }
.error { color: red; }
</style>