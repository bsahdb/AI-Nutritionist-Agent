<template>
  <div class="dashboard-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <div>
            <h2>数据看板</h2>
            <p>展示用户、体检报告、口味偏好、饮食计划和健康风险概览。</p>
          </div>

          <el-button :loading="loading" @click="loadDashboard">
            刷新数据
          </el-button>
        </div>
      </template>

      <el-row :gutter="16">
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-title">用户总数</div>
            <div class="stat-value">{{ stats.user_count }}</div>
            <div class="stat-desc">系统中的用户数量</div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-title">体检报告</div>
            <div class="stat-value">{{ stats.health_report_count }}</div>
            <div class="stat-desc">已录入的体检报告数量</div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-title">口味偏好</div>
            <div class="stat-value">{{ stats.preference_count }}</div>
            <div class="stat-desc">已设置的偏好档案数量</div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-title">饮食计划</div>
            <div class="stat-value">{{ stats.meal_plan_count }}</div>
            <div class="stat-desc">AI 已生成的饮食计划数量</div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <el-row :gutter="16">
      <el-col :span="10">
        <el-card class="section-card">
          <template #header>
            <h3>健康风险概览</h3>
          </template>

          <el-descriptions :column="1" border>
            <el-descriptions-item label="尿酸偏高报告">
              <el-tag type="warning">
                {{ riskSummary.high_uric_acid_count }} 份
              </el-tag>
            </el-descriptions-item>

            <el-descriptions-item label="血压偏高报告">
              <el-tag type="danger">
                {{ riskSummary.high_bp_count }} 份
              </el-tag>
            </el-descriptions-item>

            <el-descriptions-item label="血脂异常报告">
              <el-tag type="warning">
                {{ riskSummary.high_lipid_count }} 份
              </el-tag>
            </el-descriptions-item>

            <el-descriptions-item label="血糖异常报告">
              <el-tag type="danger">
                {{ riskSummary.high_glucose_count }} 份
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>

          <el-alert
            title="风险统计仅基于系统中已录入的体检指标，不能替代医生诊断。"
            type="info"
            show-icon
            :closable="false"
            class="mt-16"
          />
        </el-card>
      </el-col>

      <el-col :span="14">
        <el-card class="section-card">
          <template #header>
            <h3>最近饮食计划</h3>
          </template>

          <el-table
            v-loading="loading"
            :data="recentMealPlans"
            border
            empty-text="暂无饮食计划"
          >
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column prop="title" label="计划名称" min-width="220" />

            <el-table-column label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="section-card">
      <template #header>
        <h3>最近体检报告</h3>
      </template>

      <el-table
        v-loading="loading"
        :data="recentHealthReports"
        border
        empty-text="暂无体检报告"
      >
        <el-table-column prop="id" label="ID" width="70" />

        <el-table-column prop="report_name" label="报告名称" min-width="180" />

        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="空腹血糖" width="110">
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

        <el-table-column label="备注" min-width="180">
          <template #default="{ row }">
            {{ row.notes || '-' }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { getDashboardSummary } from '@/api'
import { useUserStore } from '@/stores/user'

const loading = ref(false)

const stats = reactive({
  user_count: 0,
  health_report_count: 0,
  preference_count: 0,
  meal_plan_count: 0
})

const riskSummary = reactive({
  high_uric_acid_count: 0,
  high_bp_count: 0,
  high_lipid_count: 0,
  high_glucose_count: 0
})

const recentHealthReports = ref<any[]>([])
const recentMealPlans = ref<any[]>([])
const userStore = useUserStore()
const currentUserId = computed(() => userStore.userId || 1)

async function loadDashboard() {
  loading.value = true

  try {
    const res = await getDashboardSummary(currentUserId.value)

    if (res.success) {
      const data = res.data || {}

      Object.assign(stats, data.stats || {})
      Object.assign(riskSummary, data.risk_summary || {})

      recentHealthReports.value = data.recent_health_reports || []
      recentMealPlans.value = data.recent_meal_plans || []
    } else {
      ElMessage.error(res.message || '获取数据看板失败')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('获取数据看板失败，请检查后端服务')
  } finally {
    loading.value = false
  }
}

function showValue(value: any) {
  if (value === null || value === undefined || value === '') return '-'
  return value
}

function showBloodPressure(row: any) {
  if (!row || !row.systolic_bp || !row.diastolic_bp) return '-'
  return `${row.systolic_bp}/${row.diastolic_bp}`
}

function formatDate(date?: string) {
  if (!date) return '-'
  return date.replace('T', ' ').slice(0, 19)
}

onMounted(() => {
  loadDashboard()
})
watch(
  () => currentUserId.value,
  () => {
    loadDashboard()
  }
)
</script>

<style scoped>
.dashboard-page {
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
  font-size: 22px;
}

.card-header p {
  margin: 6px 0 0;
  color: #666;
  font-size: 14px;
}

.stat-card {
  height: 130px;
}

.stat-title {
  color: #606266;
  font-size: 14px;
}

.stat-value {
  margin-top: 12px;
  font-size: 34px;
  font-weight: bold;
  color: #303133;
}

.stat-desc {
  margin-top: 8px;
  color: #909399;
  font-size: 13px;
}

.section-card {
  margin-top: 4px;
}

.section-card h3 {
  margin: 0;
  font-size: 18px;
}

.mt-16 {
  margin-top: 16px;
}
</style>