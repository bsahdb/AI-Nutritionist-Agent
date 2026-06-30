<template>
  <div class="health-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <div>
            <h2>体检报告管理</h2>
            <p>录入体检指标后，可选择某一份报告进行 AI 健康分析。</p>
          </div>

          <div>
            <el-button @click="loadReports">刷新</el-button>
            <el-button type="primary" @click="openCreateDialog">
              新增体检报告
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="reports"
        border
        style="width: 100%"
        empty-text="暂无体检报告，请先新增"
      >
        <el-table-column type="index" label="序号" width="70" />
        <el-table-column prop="id" label="报告ID" width="90" />

        <el-table-column prop="report_name" label="报告名称" min-width="180" />

        <el-table-column label="创建时间" min-width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="空腹血糖" width="100">
          <template #default="{ row }">
            {{ showValue(row.fasting_glucose) }}
          </template>
        </el-table-column>

        <el-table-column label="血压" width="110">
          <template #default="{ row }">
            {{ showBloodPressure(row) }}
          </template>
        </el-table-column>

        <el-table-column label="尿酸" width="100">
          <template #default="{ row }">
            {{ showValue(row.uric_acid) }}
          </template>
        </el-table-column>

        <el-table-column label="甘油三酯" width="110">
          <template #default="{ row }">
            {{ showValue(row.triglycerides) }}
          </template>
        </el-table-column>

        <el-table-column label="LDL" width="100">
          <template #default="{ row }">
            {{ showValue(row.ldl_cholesterol) }}
          </template>
        </el-table-column>

        <el-table-column label="备注" min-width="160">
          <template #default="{ row }">
            {{ row.notes || '-' }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openEditDialog(row)">
              编辑
            </el-button>

            <el-button
              size="small"
              type="success"
              :loading="analyzing && selectedReport?.id === row.id"
              @click="analyzeReport(row)"
            >
              AI分析
            </el-button>

            <el-button
              size="small"
              type="danger"
              @click="deleteReport(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="editingId ? '编辑体检报告' : '新增体检报告'"
      width="900px"
    >
      <el-form :model="form" label-width="120px">
        <el-row :gutter="16">
          <el-col :span="24">
            <el-form-item label="报告名称">
              <el-input v-model="form.report_name" placeholder="例如：2026年6月体检报告" />
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="空腹血糖">
              <el-input-number v-model="form.fasting_glucose" :precision="1" :step="0.1" style="width: 100%" />
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="餐后血糖">
              <el-input-number v-model="form.postprandial_glucose" :precision="1" :step="0.1" style="width: 100%" />
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="尿酸">
              <el-input-number v-model="form.uric_acid" :precision="0" :step="10" style="width: 100%" />
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="收缩压">
              <el-input-number v-model="form.systolic_bp" :precision="0" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="舒张压">
              <el-input-number v-model="form.diastolic_bp" :precision="0" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="总胆固醇">
              <el-input-number v-model="form.total_cholesterol" :precision="1" :step="0.1" style="width: 100%" />
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="甘油三酯">
              <el-input-number v-model="form.triglycerides" :precision="1" :step="0.1" style="width: 100%" />
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="HDL">
              <el-input-number v-model="form.hdl_cholesterol" :precision="1" :step="0.1" style="width: 100%" />
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="LDL">
              <el-input-number v-model="form.ldl_cholesterol" :precision="1" :step="0.1" style="width: 100%" />
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="肌酐">
              <el-input-number v-model="form.creatinine" :precision="0" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="尿素氮">
              <el-input-number v-model="form.bun" :precision="1" :step="0.1" style="width: 100%" />
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="ALT">
              <el-input-number v-model="form.alt" :precision="0" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="AST">
              <el-input-number v-model="form.ast" :precision="0" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>

          <el-col :span="8">
            <el-form-item label="血红蛋白">
              <el-input-number v-model="form.hemoglobin" :precision="0" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>

          <el-col :span="24">
            <el-form-item label="备注">
              <el-input
                v-model="form.notes"
                type="textarea"
                :rows="3"
                placeholder="例如：尿酸偏高、血脂偏高、轻度超重"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitReport">
          保存
        </el-button>
      </template>
    </el-dialog>

    <el-card v-if="analysisText" class="analysis-card">
      <template #header>
        <div class="card-header">
          <div>
            <h2>AI健康分析结果</h2>
            <p v-if="selectedReport">
              本次分析基于：{{ selectedReport.report_name }},报告ID:{{ selectedReport.id }}
            </p>
          </div>
        </div>
      </template>

      <el-alert
        title="本分析基于当前选择的体检报告和口味偏好生成，不能替代医生诊断。"
        type="warning"
        show-icon
        :closable="false"
        class="mb-16"
      />

      <el-descriptions
        v-if="analysisSource?.health_report"
        title="本次分析使用的体检数据"
        :column="3"
        border
        class="mb-16"
      >
        <el-descriptions-item label="报告名称">
          {{ analysisSource.health_report.report_name }}
        </el-descriptions-item>
        <el-descriptions-item label="空腹血糖">
          {{ showValue(analysisSource.health_report.fasting_glucose) }}
        </el-descriptions-item>
        <el-descriptions-item label="尿酸">
          {{ showValue(analysisSource.health_report.uric_acid) }}
        </el-descriptions-item>
        <el-descriptions-item label="血压">
          {{ showBloodPressure(analysisSource.health_report) }}
        </el-descriptions-item>
        <el-descriptions-item label="甘油三酯">
          {{ showValue(analysisSource.health_report.triglycerides) }}
        </el-descriptions-item>
        <el-descriptions-item label="LDL">
          {{ showValue(analysisSource.health_report.ldl_cholesterol) }}
        </el-descriptions-item>
      </el-descriptions>

      <div class="analysis-content" v-html="analysisHtml"></div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { marked } from 'marked'
import { healthApi, type HealthReport, type HealthReportForm } from '../api'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const currentUserId = computed(() => userStore.userId || 1)

const reports = ref<HealthReport[]>([])
const loading = ref(false)
const submitting = ref(false)
const analyzing = ref(false)

const dialogVisible = ref(false)
const editingId = ref<number | null>(null)

const selectedReport = ref<HealthReport | null>(null)
const analysisText = ref('')
const analysisSource = ref<any>(null)

const createEmptyForm = (): HealthReportForm => ({
  user_id: currentUserId.value,
  report_name: '',
  fasting_glucose: null,
  postprandial_glucose: null,
  total_cholesterol: null,
  triglycerides: null,
  hdl_cholesterol: null,
  ldl_cholesterol: null,
  systolic_bp: null,
  diastolic_bp: null,
  uric_acid: null,
  creatinine: null,
  bun: null,
  alt: null,
  ast: null,
  hemoglobin: null,
  notes: ''
})

const form = reactive<HealthReportForm>(createEmptyForm())

const analysisHtml = computed(() => {
  return marked.parse(analysisText.value || '') as string
})

function resetForm() {
  Object.assign(form, createEmptyForm())
  editingId.value = null
}

function showValue(value: number | string | null | undefined) {
  if (value === null || value === undefined || value === '') return '-'
  return value
}

function showBloodPressure(row: any) {
  if (!row.systolic_bp || !row.diastolic_bp) return '-'
  return `${row.systolic_bp}/${row.diastolic_bp}`
}

function formatDate(date?: string) {
  if (!date) return '-'
  return date.replace('T', ' ').slice(0, 19)
}

async function loadReports() {
  loading.value = true

  try {
    const res = await healthApi.getReports(currentUserId.value)
    reports.value = res.data.data || []
  } catch (error) {
    console.error(error)
    ElMessage.error('获取体检报告失败，请检查后端服务')
  } finally {
    loading.value = false
  }
}

function openCreateDialog() {
  resetForm()
  dialogVisible.value = true
}

function openEditDialog(row: HealthReport) {
  resetForm()
  editingId.value = row.id

  Object.assign(form, {
    user_id: row.user_id,
    report_name: row.report_name || '',
    fasting_glucose: row.fasting_glucose ?? null,
    postprandial_glucose: row.postprandial_glucose ?? null,
    total_cholesterol: row.total_cholesterol ?? null,
    triglycerides: row.triglycerides ?? null,
    hdl_cholesterol: row.hdl_cholesterol ?? null,
    ldl_cholesterol: row.ldl_cholesterol ?? null,
    systolic_bp: row.systolic_bp ?? null,
    diastolic_bp: row.diastolic_bp ?? null,
    uric_acid: row.uric_acid ?? null,
    creatinine: row.creatinine ?? null,
    bun: row.bun ?? null,
    alt: row.alt ?? null,
    ast: row.ast ?? null,
    hemoglobin: row.hemoglobin ?? null,
    notes: row.notes || ''
  })

  dialogVisible.value = true
}

async function submitReport() {
  if (!form.report_name) {
    ElMessage.warning('请输入报告名称')
    return
  }

  submitting.value = true

  try {
    if (editingId.value) {
      await healthApi.updateReport(editingId.value, form)
      ElMessage.success('体检报告更新成功')
    } else {
      await healthApi.createReport(form)
      ElMessage.success('体检报告创建成功')
    }

    dialogVisible.value = false
    await loadReports()
  } catch (error: any) {
    console.error(error)
    ElMessage.error(error?.response?.data?.detail || '保存失败')
  } finally {
    submitting.value = false
  }
}

async function deleteReport(row: HealthReport) {
  try {
    await ElMessageBox.confirm(
      `确定删除「${row.report_name || row.id}」吗？`,
      '删除确认',
      {
        type: 'warning',
        confirmButtonText: '删除',
        cancelButtonText: '取消'
      }
    )

    await healthApi.deleteReport(row.id)
    ElMessage.success('删除成功')

    if (selectedReport.value?.id === row.id) {
      selectedReport.value = null
      analysisText.value = ''
      analysisSource.value = null
    }

    await loadReports()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

async function analyzeReport(row: HealthReport) {
  selectedReport.value = row
  analysisText.value = ''
  analysisSource.value = null
  analyzing.value = true

  try {
    const res = await healthApi.analyzeHealth(currentUserId.value, row.id)

    if (!res.data.success) {
      ElMessage.error(res.data.message || 'AI分析失败')
      return
    }

    analysisSource.value = res.data.data?.data_source
    analysisText.value = res.data.data?.analysis || ''

    ElMessage.success('AI健康分析完成')
  } catch (error: any) {
    console.error(error)
    ElMessage.error(error?.response?.data?.detail || 'AI健康分析失败')
  } finally {
    analyzing.value = false
  }
}

onMounted(() => {
  loadReports()
})
watch(
  () => currentUserId.value,
  () => {
    selectedReport.value = null
    analysisText.value = ''
    analysisSource.value = null
    resetForm()
    loadReports()
  }
)
</script>

<style scoped>
.health-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
}

.card-header p {
  margin: 6px 0 0;
  color: #666;
  font-size: 14px;
}

.analysis-card {
  margin-top: 20px;
}

.mb-16 {
  margin-bottom: 16px;
}

.analysis-content {
  line-height: 1.8;
  font-size: 15px;
  background: #fff;
  padding: 16px;
  border-radius: 6px;
}

.analysis-content :deep(h1),
.analysis-content :deep(h2),
.analysis-content :deep(h3) {
  margin-top: 18px;
  margin-bottom: 10px;
}

.analysis-content :deep(ul),
.analysis-content :deep(ol) {
  padding-left: 24px;
}

</style>