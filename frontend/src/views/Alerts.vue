<template>
  <div class="alerts">
    <h2>安全告警</h2>
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-select v-model="statusFilter" placeholder="状态筛选" clearable>
          <el-option label="新" value="new"></el-option>
          <el-option label="已确认" value="acknowledged"></el-option>
          <el-option label="已解决" value="resolved"></el-option>
          <el-option label="误报" value="false_positive"></el-option>
        </el-select>
      </el-col>
      <el-col :span="6">
        <el-select v-model="severityFilter" placeholder="严重程度筛选" clearable>
          <el-option label="高危" value="high"></el-option>
          <el-option label="中危" value="medium"></el-option>
          <el-option label="低危" value="low"></el-option>
          <el-option label="信息" value="info"></el-option>
        </el-select>
      </el-col>
      <el-col :span="6">
        <el-button type="primary" @click="fetchAlerts">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </el-col>
      <el-col :span="6" style="text-align: right;">
        <el-badge :value="newAlertCount" :hidden="newAlertCount === 0">
          <el-button @click="statusFilter='new'; fetchAlerts()">新告警</el-button>
        </el-badge>
      </el-col>
    </el-row>

    <el-table :data="alerts" style="width: 100%" v-loading="loading">
      <el-table-column prop="created_at" label="时间" width="180"></el-table-column>
      <el-table-column prop="rule_name" label="规则" width="150"></el-table-column>
      <el-table-column prop="src_ip" label="源IP" width="120"></el-table-column>
      <el-table-column prop="message" label="消息" min-width="200"></el-table-column>
      <el-table-column prop="severity" label="严重程度" width="100">
        <template #default="scope">
          <el-tag :type="severityTag(scope.row.severity)">{{ scope.row.severity }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="120">
        <template #default="scope">
          <el-select v-model="scope.row.status" @change="updateStatus(scope.row)" size="small">
            <el-option label="新" value="new"></el-option>
            <el-option label="已确认" value="acknowledged"></el-option>
            <el-option label="已解决" value="resolved"></el-option>
            <el-option label="误报" value="false_positive"></el-option>
          </el-select>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      @current-change="handlePageChange"
      :current-page="currentPage"
      :page-size="perPage"
      layout="total, prev, pager, next"
      :total="total">
    </el-pagination>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      alerts: [],
      loading: false,
      statusFilter: '',
      severityFilter: '',
      currentPage: 1,
      perPage: 20,
      total: 0,
      newAlertCount: 0
    }
  },
  created() {
    this.fetchAlerts()
    this.fetchStats()
    // 定时刷新
    this.timer = setInterval(() => {
      this.fetchAlerts()
      this.fetchStats()
    }, 10000)
  },
  beforeUnmount() {
    if (this.timer) clearInterval(this.timer)
  },
  methods: {
    async fetchAlerts() {
      this.loading = true
      try {
        const params = {
          page: this.currentPage,
          per_page: this.perPage
        }
        if (this.statusFilter) params.status = this.statusFilter
        if ( this.severityFilter) params.severity = this.severityFilter

        const res = await axios.get('/api/alerts', { params })
        if (res.data.code === 200) {
          this.alerts = res.data.data
          this.total = res.data.total
        }
      } catch (err) {
        this.$message.error('获取告警失败')
        console.error(err)
      } finally {
        this.loading = false
      }
    },
    async fetchStats() {
      try {
        const res = await axios.get('/api/alerts/stats')
        if (res.data.code === 200) {
          this.newAlertCount = res.data.data.new
        }
      } catch (err) {
        console.error('获取统计失败', err)
      }
    },
    async updateStatus(alert) {
      try {
        await axios.put(`/api/alerts/${alert.id}`, { status: alert.status })
        this.$message.success('状态更新成功')
        this.fetchStats() // 更新统计
      } catch (err) {
        this.$message.error('更新失败')
        // 回滚状态（可选）
        const oldStatus = this.alerts.find(a => a.id === alert.id)?.status
        if (oldStatus) alert.status = oldStatus
      }
    },
    handlePageChange(page) {
      this.currentPage = page
      this.fetchAlerts()
    },
    resetFilters() {
      this.statusFilter = ''
      this.severityFilter = ''
      this.currentPage = 1
      this.fetchAlerts()
    },
    severityTag(severity) {
      const map = {
        'high': 'danger',
        'medium': 'warning',
        'low': 'info',
        'info': ''
      }
      return map[severity] || ''
    }
  },
  watch: {
    statusFilter() {
      this.currentPage = 1
      this.fetchAlerts()
    },
    severityFilter() {
      this.currentPage = 1
      this.fetchAlerts()
    }
  }
}
</script>

<style scoped>
.alerts {
  padding: 20px;
}
</style>