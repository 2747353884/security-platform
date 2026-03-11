<template>
  <div class="home">
    <h1>网络安全态势感知平台</h1>
    <p v-if="user">欢迎，{{ user.username }}！</p>
    <p v-else>
      <router-link to="/login">登录</router-link> | 
      <router-link to="/register">注册</router-link>
    </p>
  </div>
</template>

<script>
export default {
  computed: {
    user() {
      const userStr = localStorage.getItem('user')
      return userStr ? JSON.parse(userStr) : null
    }
  }
}
</script>