<template>
  <div id="app">
    <nav v-if="user">
      <span>欢迎，{{ user.username }}</span>
      <div class="nav-links">
        <router-link to="/">首页</router-link> |
        <router-link to="/assets">资产管理</router-link> |
        <router-link to="/vulnerabilities">漏洞列表</router-link> |
        <router-link to="/scan">发起扫描</router-link> |
        <button @click="logout">注销</button>
      </div>
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
.nav-links a {
  margin: 0 10px;
  text-decoration: none;
  color: #1890ff;
}
.nav-links a.router-link-active {
  font-weight: bold;
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