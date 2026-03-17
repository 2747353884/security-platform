<template>
  <div class="rules">
    <h2>规则管理</h2>
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="24">
        <el-button type="primary" @click="openCreateDialog">新建规则</el-button>
      </el-col>
    </el-row>

    <el-table :data="rules" style="width: 100%" v-loading="loading">
      <el-table-column prop="id" label="ID" width="80"></el-table-column>
      <el-table-column prop="name" label="规则名称" width="150"></el-table-column>
      <el-table-column prop="description" label="描述" min-width="200"></el-table-column>
      <el-table-column prop="rule_type" label="类型" width="100">
        <template #default="scope">
          <el-tag>{{ scope.row.rule_type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="pattern" label="模式" min-width="200"></el-table-column>
      <el-table-column prop="severity" label="严重程度" width="100">
        <template #default="scope">
          <el-tag :type="severityTag(scope.row.severity)">{{ scope.row.severity }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="enabled" label="启用" width="80">
        <template #default="scope">
          <el-switch v-model="scope.row.enabled" @change="toggleEnabled(scope.row)"></el-switch>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="scope">
          <el-button size="small" @click="editRule(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteRule(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建/编辑规则对话框 -->
    <el-dialog :title="dialogTitle" v-model="dialogVisible" width="600px">
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="规则名称" prop="name">
          <el-input v-model="form.name" placeholder="输入规则名称"></el-input>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="输入规则描述"></el-input>
        </el-form-item>
        <el-form-item label="规则类型" prop="rule_type">
          <el-select v-model="form.rule_type" placeholder="选择类型">
            <el-option label="正则匹配" value="regex"></el-option>
            <el-option label="阈值匹配" value="threshold"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="匹配模式" prop="pattern">
          <el-input v-model="form.pattern" placeholder="输入正则表达式或条件" type="textarea" :rows="2"></el-input>
          <div class="el-form-item-msg" v-if="form.rule_type === 'regex'">例如: Failed password</div>
        </el-form-item>
        <el-form-item label="严重程度" prop="severity">
          <el-select v-model="form.severity" placeholder="选择严重程度">
            <el-option label="高危" value="high"></el-option>
            <el-option label="中危" value="medium"></el-option>
            <el-option label="低危" value="low"></el-option>
            <el-option label="信息" value="info"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="启用" prop="enabled">
          <el-switch v-model="form.enabled"></el-switch>
        </el-form-item>
        <template v-if="form.rule_type === 'threshold'">
          <el-form-item label="阈值次数" prop="threshold_count">
            <el-input-number v-model="form.threshold_count" :min="1" :max="100"></el-input-number>
          </el-form-item>
          <el-form-item label="时间窗口(秒)" prop="threshold_seconds">
            <el-input-number v-model="form.threshold_seconds" :min="1" :max="3600"></el-input-number>
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      rules: [],
      loading: false,
      dialogVisible: false,
      dialogTitle: '新建规则',
      form: {
        name: '',
        description: '',
        rule_type: 'regex',
        pattern: '',
        severity: 'medium',
        enabled: true,
        threshold_count: 5,
        threshold_seconds: 300
      },
      formRules: {
        name: [{ required: true, message: '请输入规则名称', trigger: 'blur' }],
        pattern: [{ required: true, message: '请输入匹配模式', trigger: 'blur' }]
      },
      editingId: null
    }
  },
  created() {
    this.fetchRules()
  },
  methods: {
    async fetchRules() {
      this.loading = true
      try {
        const res = await axios.get('/api/rules')
        if (res.data.code === 200) {
          this.rules = res.data.data
        }
      } catch (err) {
        this.$message.error('获取规则列表失败')
        console.error(err)
      } finally {
        this.loading = false
      }
    },
    openCreateDialog() {
      this.dialogTitle = '新建规则'
      this.editingId = null
      this.form = {
        name: '',
        description: '',
        rule_type: 'regex',
        pattern: '',
        severity: 'medium',
        enabled: true,
        threshold_count: 5,
        threshold_seconds: 300
      }
      this.dialogVisible = true
    },
    editRule(rule) {
      this.dialogTitle = '编辑规则'
      this.editingId = rule.id
      this.form = { ...rule }  // 浅拷贝
      this.dialogVisible = true
    },
    async submitForm() {
      this.$refs.formRef.validate(async (valid) => {
        if (!valid) return
        try {
          if (this.editingId) {
            // 更新
            await axios.put(`/api/rules/${this.editingId}`, this.form)
            this.$message.success('更新成功')
          } else {
            // 创建
            await axios.post('/api/rules', this.form)
            this.$message.success('创建成功')
          }
          this.dialogVisible = false
          this.fetchRules()
        } catch (err) {
          this.$message.error(err.response?.data?.msg || '操作失败')
        }
      })
    },
    async deleteRule(rule) {
      this.$confirm(`确定删除规则 "${rule.name}" 吗？`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await axios.delete(`/api/rules/${rule.id}`)
          this.$message.success('删除成功')
          this.fetchRules()
        } catch (err) {
          this.$message.error(err.response?.data?.msg || '删除失败')
        }
      }).catch(() => {})
    },
    async toggleEnabled(rule) {
      try {
        await axios.put(`/api/rules/${rule.id}`, { enabled: rule.enabled })
        this.$message.success('状态更新成功')
      } catch (err) {
        this.$message.error('更新失败')
        // 回滚状态
        rule.enabled = !rule.enabled
      }
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
  }
}
</script>

<style scoped>
.rules {
  padding: 20px;
}
.el-form-item-msg {
  color: #999;
  font-size: 12px;
  margin-top: 5px;
}
</style>