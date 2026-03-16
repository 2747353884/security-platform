<template>
  <div class="scan">
    <h2>发起网络扫描</h2>
    <el-form :model="form" label-width="100px">
      <el-form-item label="扫描目标">
        <el-input v-model="form.target" placeholder="例如: 192.168.1.0/24" style="width: 300px"></el-input>
        <div class="el-form-item-extra">支持单个IP (如 192.168.1.1) 或网段 (如 192.168.1.0/24)</div>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="startScan" :loading="scanning">开始扫描</el-button>
      </el-form-item>
    </el-form>
    
    <div v-if="taskId" style="margin-top: 20px">
      <h3>扫描进度</h3>
      <el-progress :percentage="progress" :status="progressStatus"></el-progress>
      <p>{{ statusMessage }}</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  data() {
    return {
      form: {
        target: ''
      },
      scanning: false,
      taskId: null,
      progress: 0,
      statusMessage: '',
      timer: null
    }
  },
  computed: {
    progressStatus() {
      if (this.progress >= 100) return 'success'
      if (this.progress > 0) return ''
      return ''
    }
  },
  methods: {
    async startScan() {
      if (!this.form.target) {
        this.$message.error('请输入扫描目标')
        return
      }
      this.scanning = true
      try {
        const res = await axios.post('/api/scan/start', { target: this.form.target })
        if (res.data.code === 200) {
          this.taskId = res.data.data.task_id
          this.$message.success('扫描任务已启动')
          this.pollStatus()
        } else {
          this.$message.error(res.data.msg || '启动扫描失败')
          this.scanning = false
        }
      } catch (err) {
        this.$message.error('启动扫描失败：' + (err.response?.data?.msg || err.message))
        this.scanning = false
      }
    },
    pollStatus() {
      this.timer = setInterval(async () => {
        try {
          const res = await axios.get(`/api/scan/status/${this.taskId}`)
          if (res.data.code === 200) {
            const data = res.data.data
            this.progress = data.current || 0
            this.statusMessage = data.status || ''
            if (data.state === 'SUCCESS') {
              clearInterval(this.timer)
              this.scanning = false
              this.$message.success('扫描完成')
              // 可选：跳转到资产列表
              this.$router.push('/assets')
            } else if (data.state === 'FAILURE') {
              clearInterval(this.timer)
              this.scanning = false
              this.$message.error('扫描失败')
            }
          }
        } catch (err) {
          console.error('查询状态失败', err)
          // 如果连续失败，可以停止轮询
          // clearInterval(this.timer)
          // this.scanning = false
        }
      }, 2000)
    }
  },
  beforeUnmount() {
    if (this.timer) clearInterval(this.timer)
  }
}
</script>

<style scoped>
.el-form-item-extra {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>