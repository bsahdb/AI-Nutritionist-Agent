<template>
  <div class="meal-plan-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <div>
            <h2>饮食计划生成</h2>
            <p>选择体检报告和生成参数，AI 会结合体检数据与口味偏好生成个性化饮食计划。</p>
          </div>

          <el-button @click="loadPlans">刷新历史计划</el-button>
        </div>
      </template>

      <el-form :model="form" label-width="120px" class="generate-form">
        <el-form-item label="体检报告">
          <el-select
            v-model="form.report_id"
            placeholder="请选择体检报告"
            style="width: 100%"
          >
            <el-option
              v-for="report in reports"
              :key="report.id"
              :label="`${report.report_name || '未命名报告'}（ID:${report.id}）`"
              :value="report.id"
            />
          </el-select>
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="6">
            <el-form-item label="生成天数">
              <el-input-number v-model="form.days" :min="1" :max="14" style="width: 100%" />
            </el-form-item>
          </el-col>

          <el-col :span="6">
            <el-form-item label="每日餐次">
              <el-input-number v-model="form.meal_count" :min="2" :max="6" style="width: 100%" />
            </el-form-item>
          </el-col>

          <el-col :span="6">
            <el-form-item label="目标热量">
              <el-input-number
                v-model="form.target_calories"
                :min="1000"
                :max="4000"
                :step="100"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>

          <el-col :span="6">
            <el-form-item label="计划标题">
              <el-input v-model="form.title" placeholder="可选" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="额外要求">
          <el-input
            v-model="form.requirements"
            type="textarea"
            :rows="3"
            placeholder="例如：低嘌呤、低盐、低脂、适合上班族、准备简单"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            :loading="generating"
            @click="handleGenerate"
          >
            生成饮食计划
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="currentPlan" class="result-card">
      <template #header>
        <div class="card-header">
          <div>
            <h2>{{ currentPlan.title }}</h2>
            <p>计划ID：{{ currentPlan.id }}，创建时间：{{ formatDate(currentPlan.created_at) }}</p>
          </div>
        </div>
      </template>

      <el-descriptions
        v-if="currentPlan.plan_data?.data_source?.health_report"
        title="本计划依据的体检报告"
        :column="3"
        border
        class="mb-16"
      >
        <el-descriptions-item label="报告名称">
          {{ currentPlan.plan_data.data_source.health_report.report_name }}
        </el-descriptions-item>
        <el-descriptions-item label="血压">
          {{ showBloodPressure(currentPlan.plan_data.data_source.health_report) }}
        </el-descriptions-item>
        <el-descriptions-item label="尿酸">
          {{ showValue(currentPlan.plan_data.data_source.health_report.uric_acid) }}
        </el-descriptions-item>
        <el-descriptions-item label="空腹血糖">
          {{ showValue(currentPlan.plan_data.data_source.health_report.fasting_glucose) }}
        </el-descriptions-item>
        <el-descriptions-item label="甘油三酯">
          {{ showValue(currentPlan.plan_data.data_source.health_report.triglycerides) }}
        </el-descriptions-item>
        <el-descriptions-item label="LDL">
          {{ showValue(currentPlan.plan_data.data_source.health_report.ldl_cholesterol) }}
        </el-descriptions-item>
      </el-descriptions>

      <el-alert
        title="饮食计划仅用于健康管理参考，不能替代医生诊断和治疗。"
        type="warning"
        show-icon
        :closable="false"
        class="mb-16"
      />

      <div v-if="currentPlan.health_summary" class="section">
        <h3>健康摘要</h3>
        <pre>{{ prettyJson(currentPlan.health_summary) }}</pre>
      </div>

      <div v-if="currentPlan.nutrition_goals" class="section">
        <h3>营养目标</h3>
        <pre>{{ prettyJson(currentPlan.nutrition_goals) }}</pre>
      </div>

      <div v-if="days.length > 0" class="section">
        <h3>每日饮食安排</h3>

        <el-collapse>
          <el-collapse-item
            v-for="day in days"
            :key="day.day"
            :title="`第 ${day.day} 天：${day.theme || ''}`"
            :name="day.day"
          >
            <div
              v-for="meal in day.meals || []"
              :key="meal.meal"
              class="meal-item"
            >
              <h4>{{ meal.meal }}</h4>
              <p><strong>食物：</strong>{{ joinList(meal.foods) }}</p>
              <p><strong>说明：</strong>{{ meal.notes || '-' }}</p>
            </div>

            <div v-if="day.tips?.length">
              <h4>当天注意事项</h4>
              <ul>
                <li v-for="tip in day.tips" :key="tip">{{ tip }}</li>
              </ul>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>

      <div v-if="currentPlan.shopping_list?.length" class="section">
        <h3>购物清单</h3>
        <el-tag
          v-for="item in currentPlan.shopping_list"
          :key="item"
          class="tag-item"
        >
          {{ item }}
        </el-tag>
      </div>

      <div v-if="currentPlan.plan_data?.raw_text" class="section">
        <h3>原始内容</h3>
        <pre>{{ currentPlan.plan_data.raw_text }}</pre>
      </div>
    </el-card>

    <el-card class="history-card">
      <template #header>
        <h2>历史饮食计划</h2>
      </template>

      <el-table
        v-loading="plansLoading"
        :data="plans"
        border
        empty-text="暂无饮食计划"
      >
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="title" label="标题" min-width="220" />

        <el-table-column label="创建时间" min-width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="天数" width="100">
          <template #default="{ row }">
            {{ row.plan_data?.days?.length || 0 }} 天
          </template>
        </el-table-column>

        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button size="small" @click="viewPlan(row)">
              查看
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  deleteMealPlan,
  generateMealPlan,
  getHealthReports,
  listMealPlans
} from '@/api'
import { useUserStore } from '@/stores/user'


const userStore = useUserStore()
const currentUserId = computed(() => userStore.userId || 1)

const reports = ref<any[]>([])
const plans = ref<any[]>([])
const currentPlan = ref<any>(null)

const generating = ref(false)
const plansLoading = ref(false)

const form = reactive({
  report_id: null as number | null,
  days: 7,
  meal_count: 3,
  target_calories: null as number | null,
  requirements: '',
  title: ''
})

const days = computed(() => {
  return currentPlan.value?.plan_data?.days || []
})

async function loadReports() {
  try {
    const res = await getHealthReports(currentUserId.value)

    if (res.success) {
      reports.value = res.data || []

      if (!form.report_id && reports.value.length > 0) {
        form.report_id = reports.value[0].id
      }
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('获取体检报告失败')
  }
}

async function loadPlans() {
  plansLoading.value = true

  try {
    const res = await listMealPlans(currentUserId.value)

    if (res.success) {
      plans.value = res.data || []

      if (!currentPlan.value && plans.value.length > 0) {
        currentPlan.value = plans.value[0]
      }
    } else {
      ElMessage.error(res.message || '获取饮食计划失败')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('获取饮食计划失败')
  } finally {
    plansLoading.value = false
  }
}

async function handleGenerate() {
  if (!form.report_id) {
    ElMessage.warning('请先选择体检报告')
    return
  }

  generating.value = true

  try {
    const res = await generateMealPlan({
      user_id: currentUserId.value,
      report_id: form.report_id,
      days: form.days,
      meal_count: form.meal_count,
      target_calories: form.target_calories,
      requirements: form.requirements,
      title: form.title
    })

    if (res.success) {
      ElMessage.success('饮食计划生成成功')
      currentPlan.value = res.data
      await loadPlans()
    } else {
      ElMessage.error(res.message || '饮食计划生成失败')
    }
  } catch (error: any) {
    console.error(error)
    ElMessage.error(error?.response?.data?.detail || '饮食计划生成失败')
  } finally {
    generating.value = false
  }
}

function viewPlan(row: any) {
  currentPlan.value = row
}

async function handleDelete(row: any) {
  try {
    await ElMessageBox.confirm(
      `确定删除「${row.title || row.id}」吗？`,
      '删除确认',
      {
        type: 'warning',
        confirmButtonText: '删除',
        cancelButtonText: '取消'
      }
    )

    await deleteMealPlan(row.id)
    ElMessage.success('删除成功')

    if (currentPlan.value?.id === row.id) {
      currentPlan.value = null
    }

    await loadPlans()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

function prettyJson(value: any) {
  if (!value) return '-'

  if (typeof value === 'string') return value

  return JSON.stringify(value, null, 2)
}

function joinList(list: any[]) {
  return list && list.length > 0 ? list.join('、') : '-'
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

onMounted(async () => {
  await loadReports()
  await loadPlans()
})

watch(
  () => currentUserId.value,
  async () => {
    reports.value = []
    plans.value = []
    currentPlan.value = null
    form.report_id = null

    await loadReports()
    await loadPlans()
  }
)
</script>

<style scoped>
.meal-plan-page {
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

.generate-form {
  max-width: 1100px;
}

.result-card,
.history-card {
  margin-top: 4px;
}

.mb-16 {
  margin-bottom: 16px;
}

.section {
  margin-top: 20px;
}

.section h3 {
  margin-bottom: 12px;
}

pre {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 6px;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
}

.meal-item {
  padding: 12px;
  margin-bottom: 12px;
  background: #f8fafc;
  border-radius: 6px;
}

.meal-item h4 {
  margin: 0 0 8px;
}

.tag-item {
  margin: 0 8px 8px 0;
}
</style>