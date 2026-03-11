<template>
  <div id="app">
    <nav v-if="user">
      <span>欢迎，{{ user.username }}</span>
      <button @click="logout">注销</button>
    </nav>
    <router-view />
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'App',
  data() {
    return {
      user: JSON.parse(localStorage.getItem('user')) || null
    }
  },
  methods: {
    async logout() {
      try {
        await axios.post('/api/logout')
        localStorage.removeItem('user')
        this.user = null
        this.$router.push('/login')
      } catch (err) {
        console.error('注销失败', err)
      }
    }
  },
  watch: {
    // 监听路由变化，如果 user 信息在 localStorage 中改变，可以重新获取
    $route() {
      this.user = JSON.parse(localStorage.getItem('user')) || null
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  color: #2c3e50;
  margin-top: 20px;
}
nav {
  background: #f0f2f5;
  padding: 10px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
nav button {
  background: #ff4d4f;
  color: white;
  border: none;
  padding: 5px 15px;
  border-radius: 4px;
  cursor: pointer;
}
</style>