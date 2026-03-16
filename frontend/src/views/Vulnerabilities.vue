<template>
  <div class="vulnerabilities">
    <h2>漏洞列表</h2>
    <el-table :data="vulnerabilities" style="width: 100%">
      <el-table-column prop="cve_id" label="CVE编号" width="150"></el-table-column>
      <el-table-column prop="description" label="描述" min-width="300"></el-table-column>
      <el-table-column prop="cvss_score" label="CVSS评分" width="100"></el-table-column>
      <el-table-column prop="severity" label="严重程度" width="100">
        <template #default="scope">
          <el-tag :type="severityTag(scope.row.severity)">{{ scope.row.severity }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="asset_ip" label="所属资产" width="150"></el-table-column>
      <el-table-column prop="port" label="端口" width="80"></el-table-column>
      <el-table-column prop="protocol" label="协议" width="80"></el-table-column>
    </el-table>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  data() {
    return {
      vulnerabilities: []
    }
  },
  created() {
    this.fetchVulns()
  },
  methods: {
    async fetchVulns() {
      try {
        const res = await axios.get('/api/vulnerabilities')
        if (res.data.code === 200) {
          this.vulnerabilities = res.data.data
        }
      } catch (err) {
        console.error('获取漏洞列表失败', err)
      }
    },
    severityTag(severity) {
      if (severity === '高危') return 'danger'
      if (severity === '中危') return 'warning'
      return 'info'
    }
  }
}
</script>