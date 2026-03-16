<template>
  <div class="asset-detail">
    <h2>资产详情 - {{ asset?.ip }}</h2>
    <el-card v-if="asset">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="IP地址">{{ asset.ip }}</el-descriptions-item>
        <el-descriptions-item label="主机名">{{ asset.hostname || '无' }}</el-descriptions-item>
        <el-descriptions-item label="操作系统">{{ asset.os }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="asset.status === 'up' ? 'success' : 'danger'">{{ asset.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="风险评分">{{ asset.risk_score }}</el-descriptions-item>
        <el-descriptions-item label="发现时间">{{ asset.discovered_at }}</el-descriptions-item>
        <el-descriptions-item label="最后扫描">{{ asset.last_scan }}</el-descriptions-item>
      </el-descriptions>
      
      <h3 style="margin-top: 20px;">开放端口</h3>
      <el-table :data="asset.ports" style="width: 100%">
        <el-table-column prop="port" label="端口" width="100"></el-table-column>
        <el-table-column prop="protocol" label="协议" width="80"></el-table-column>
        <el-table-column prop="service" label="服务" width="120"></el-table-column>
        <el-table-column prop="version" label="版本"></el-table-column>
        <el-table-column prop="state" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.state === 'open' ? 'success' : 'info'">
              {{ scope.row.state }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="漏洞" width="150">
          <template #default="scope">
            <el-badge :value="scope.row.vulnerabilities.length" :hidden="scope.row.vulnerabilities.length === 0">
              <el-button size="small" @click="showVulns(scope.row)">查看漏洞</el-button>
            </el-badge>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="vulnDialogVisible" title="漏洞详情" width="70%">
      <el-table :data="currentPortVulns" style="width: 100%">
        <el-table-column prop="cve_id" label="CVE编号" width="150"></el-table-column>
        <el-table-column prop="description" label="描述" min-width="300"></el-table-column>
        <el-table-column prop="cvss_score" label="CVSS评分" width="100"></el-table-column>
        <el-table-column prop="severity" label="严重程度" width="100">
          <template #default="scope">
            <el-tag :type="severityTag(scope.row.severity)">{{ scope.row.severity }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  props: ['id'],
  data() {
    return {
      asset: null,
      vulnDialogVisible: false,
      currentPortVulns: []
    }
  },
  created() {
    this.fetchAsset()
  },
  methods: {
    async fetchAsset() {
      try {
        const res = await axios.get(`/api/assets/${this.id}`)
        if (res.data.code === 200) {
          this.asset = res.data.data
        }
      } catch (err) {
        console.error('获取资产详情失败', err)
      }
    },
    showVulns(port) {
      this.currentPortVulns = port.vulnerabilities
      this.vulnDialogVisible = true
    },
    severityTag(severity) {
      if (severity === '高危') return 'danger'
      if (severity === '中危') return 'warning'
      return 'info'
    }
  }
}
</script>