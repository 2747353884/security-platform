<template>
  <div class="assets">
    <h2>资产管理</h2>
    <el-table :data="assets" style="width: 100%">
      <el-table-column prop="ip" label="IP地址" width="180"></el-table-column>
      <el-table-column prop="hostname" label="主机名" width="180"></el-table-column>
      <el-table-column prop="os" label="操作系统"></el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.status === 'up' ? 'success' : 'danger'">
            {{ scope.row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="risk_score" label="风险评分" width="120">
        <template #default="scope">
          <el-rate v-model="scope.row.risk_score" disabled show-score text-color="#ff9900" score-template="{value}">
          </el-rate>
        </template>
      </el-table-column>
      <el-table-column prop="ports_count" label="端口数" width="100"></el-table-column>
      <el-table-column prop="last_scan" label="最后扫描" width="200"></el-table-column>
      <el-table-column label="操作" width="150">
        <template #default="scope">
          <el-button size="small" @click="viewDetail(scope.row.id)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  data() {
    return {
      assets: []
    }
  },
  created() {
    this.fetchAssets()
  },
  methods: {
    async fetchAssets() {
      try {
        const res = await axios.get('/api/assets')
        if (res.data.code === 200) {
          this.assets = res.data.data
        }
      } catch (err) {
        console.error('获取资产失败', err)
      }
    },
    viewDetail(id) {
      this.$router.push(`/assets/${id}`)
    }
  }
}
</script>