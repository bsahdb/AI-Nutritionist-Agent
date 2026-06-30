<template>
  <div class="chat-page">
    <div class="chat-sidebar">
      <h3>💬 AI营养师对话</h3>

      <div class="report-select-box">
        <div class="select-label">当前体检报告</div>

        <el-select
          v-model="selectedReportId"
          placeholder="请选择体检报告"
          style="width: 100%;"
          :disabled="reportsLoading"
        >
          <el-option
            v-for="report in reports"
            :key="report.id"
            :label="`${report.report_name || '未命名报告'}(ID:${report.id})`"
            :value="report.id"
          />
        </el-select>

        <el-button
          style="width: 100%; margin-top: 8px;"
          @click="loadReports"
        >
          刷新报告
        </el-button>

        <el-alert
          v-if="!reportsLoading && reports.length === 0"
          title="暂无体检报告，请先到“体检报告”页面录入。"
          type="warning"
          show-icon
          :closable="false"
          style="margin-top: 8px;"
        />
      </div>

      <el-button
        type="primary"
        style="width: 100%; margin-top: 16px;"
        :disabled="!selectedReportId"
        :loading="thinking"
        @click="handleAnalyze"
      >
        <el-icon><DataAnalysis /></el-icon>
        AI健康分析
      </el-button>

      <div v-if="selectedReport" class="current-report">
        <h4>当前分析报告</h4>
        <p>名称：{{ selectedReport.report_name || '-' }}</p>
        <p>ID：{{ selectedReport.id }}</p>
        <p>血压：{{ showBloodPressure(selectedReport) }}</p>
        <p>尿酸：{{ showValue(selectedReport.uric_acid) }}</p>
        <p>空腹血糖：{{ showValue(selectedReport.fasting_glucose) }}</p>
      </div>

      <div class="quick-questions">
        <h4>常见问题</h4>
        <div
          v-for="q in quickQuestions"
          :key="q"
          class="quick-question-item"
          @click="sendQuickQuestion(q)"
        >
          {{ q }}
        </div>
      </div>
    </div>

    <div class="chat-main">
      <div class="chat-messages" ref="messagesRef">
        <div v-if="messages.length === 0" class="welcome-message">
          <h2>你好!我是你的AI营养师 🥗</h2>
          <p>我可以根据你选择的体检报告和口味偏好，提供个性化的营养建议。</p>
          <p>请先在左侧选择一份体检报告,然后点击“AI健康分析”或直接提问。</p>
        </div>

        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          :class="['chat-bubble', msg.role]"
        >
          <div class="bubble-content" v-html="formatMessage(msg.content)" />
        </div>

        <div v-if="thinking" class="chat-bubble assistant">
          <div class="thinking">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </div>
        </div>
      </div>

      <div class="chat-input-area">
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="2"
          placeholder="输入您的问题，例如：高尿酸患者能吃什么？"
          :disabled="thinking"
          @keydown.enter.exact.prevent="handleSend"
        />

        <el-button
          type="primary"
          :loading="thinking"
          @click="handleSend"
          style="margin-top: 8px;"
        >
          <el-icon><Promotion /></el-icon>
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { agentChat, analyzeHealth, getHealthReports } from '@/api'
import { useUserStore } from '@/stores/user'
import { DataAnalysis, Promotion } from '@element-plus/icons-vue'
import { marked } from 'marked'

const userStore = useUserStore()

const currentUserId = computed(() => userStore.userId || 1)

const messages = ref<any[]>([])
const inputMessage = ref('')
const thinking = ref(false)
const messagesRef = ref()

const reports = ref<any[]>([])
const reportsLoading = ref(false)
const selectedReportId = ref<number | null>(null)

const selectedReport = computed(() => {
  return reports.value.find(item => item.id === selectedReportId.value) || null
})

const quickQuestions = [
  '高血压患者应该吃什么？',
  '糖尿病饮食注意事项',
  '减肥期间怎么吃？',
  '高尿酸患者能吃什么？'
]

async function loadReports() {
  reportsLoading.value = true

  try {
    const res = await getHealthReports(currentUserId.value)

    if (res.success) {
      reports.value = res.data || []

      if (!selectedReportId.value && reports.value.length > 0) {
        selectedReportId.value = reports.value[0].id
      }
    } else {
      ElMessage.error(res.message || '获取体检报告失败')
    }
  } catch (e) {
    console.error('获取体检报告失败：', e)
    ElMessage.error('获取体检报告失败，请检查后端服务')
  } finally {
    reportsLoading.value = false
  }
}

function checkSelectedReport() {
  if (!selectedReportId.value) {
    ElMessage.warning('请先选择一份体检报告')
    return false
  }

  return true
}

async function handleSend() {
  if (!inputMessage.value.trim() || thinking.value) return
  if (!checkSelectedReport()) return

  const userMsg = inputMessage.value.trim()

  messages.value.push({
    role: 'user',
    content: userMsg
  })

  inputMessage.value = ''
  thinking.value = true
  scrollToBottom()

  try {
    const res = await agentChat(
      currentUserId.value,
      userMsg,
      selectedReportId.value || undefined
    )

    if (res.success) {
      messages.value.push({
        role: 'assistant',
        content: res.data?.reply || 'AI 已返回，但内容为空。'
      })
    } else {
      messages.value.push({
        role: 'assistant',
        content: res.message || '抱歉，服务暂时不可用，请稍后再试。'
      })
    }
  } catch (e) {
    console.error('AI对话接口调用失败：', e)

    messages.value.push({
      role: 'assistant',
      content: '抱歉，AI对话服务暂时不可用，请检查后端服务或大模型配置。'
    })
  } finally {
    thinking.value = false
    scrollToBottom()
  }
}

async function handleAnalyze() {
  if (thinking.value) return
  if (!checkSelectedReport()) return

  thinking.value = true

  const reportName = selectedReport.value?.report_name || `报告ID：${selectedReportId.value}`

  messages.value.push({
    role: 'user',
    content: `请基于「${reportName}」进行 AI 健康分析。`
  })

  scrollToBottom()

  try {
    const res = await analyzeHealth(
      currentUserId.value,
      selectedReportId.value as number
    )

    if (res.success) {
      const source = res.data?.data_source?.health_report

      const sourceText = source
        ? `\n\n---\n\n**本次分析依据**\n\n- 报告名称：${source.report_name || '-'}\n- 报告ID：${source.id}\n- 空腹血糖：${showValue(source.fasting_glucose)}\n- 血压：${showBloodPressure(source)}\n- 尿酸：${showValue(source.uric_acid)}\n- 甘油三酯：${showValue(source.triglycerides)}\n- LDL：${showValue(source.ldl_cholesterol)}\n\n---\n\n`
        : ''

      messages.value.push({
        role: 'assistant',
        content: `${sourceText}${res.data?.analysis || 'AI分析完成，但内容为空。'}`
      })
    } else {
      messages.value.push({
        role: 'assistant',
        content: res.message || '健康分析失败，请稍后再试。'
      })
    }
  } catch (e) {
    console.error('健康分析接口调用失败：', e)

    messages.value.push({
      role: 'assistant',
      content: '健康分析失败，请检查后端服务或大模型 API 配置。'
    })
  } finally {
    thinking.value = false
    scrollToBottom()
  }
}

function sendQuickQuestion(q: string) {
  if (thinking.value) return

  inputMessage.value = q
  handleSend()
}

function formatMessage(content: string) {
  return marked.parse(content || '')
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

function showValue(value: number | string | null | undefined) {
  if (value === null || value === undefined || value === '') return '-'
  return value
}

function showBloodPressure(row: any) {
  if (!row || !row.systolic_bp || !row.diastolic_bp) return '-'
  return `${row.systolic_bp}/${row.diastolic_bp}`
}

onMounted(() => {
  loadReports()
})
watch(
  () => currentUserId.value,
  async () => {
    messages.value = []
    inputMessage.value = ''
    selectedReportId.value = null
    reports.value = []
    await loadReports()
  }
)
</script>

<style scoped>
.chat-page {
  display: flex;
  height: calc(100vh - 110px);
  gap: 16px;
}

.chat-sidebar {
  width: 300px;
  background: #ffffff;
  border-radius: 8px;
  padding: 16px;
  overflow-y: auto;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border-radius: 8px;
  overflow: hidden;
}

.report-select-box {
  margin-top: 12px;
}

.select-label {
  font-weight: bold;
  margin-bottom: 8px;
}

.current-report {
  margin-top: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
  font-size: 14px;
}

.current-report h4 {
  margin: 0 0 8px;
}

.current-report p {
  margin: 4px 0;
}

.quick-questions {
  margin-top: 20px;
}

.quick-question-item {
  padding: 10px;
  margin-bottom: 8px;
  background: #f5f7fa;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.quick-question-item:hover {
  background: #e8f3ff;
  color: #409eff;
}

.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.welcome-message {
  color: #333;
}

.chat-bubble {
  margin-bottom: 16px;
  display: flex;
}

.chat-bubble.user {
  justify-content: flex-end;
}

.chat-bubble.assistant {
  justify-content: flex-start;
}

.bubble-content {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 8px;
  line-height: 1.8;
  word-break: break-word;
}

.chat-bubble.user .bubble-content {
  background: #409eff;
  color: #ffffff;
}

.chat-bubble.assistant .bubble-content {
  background: #f5f7fa;
  color: #303133;
}

.bubble-content :deep(p) {
  margin: 6px 0;
}

.bubble-content :deep(ul),
.bubble-content :deep(ol) {
  padding-left: 22px;
}

.chat-input-area {
  padding: 16px;
  border-top: 1px solid #e5e7eb;
}

.thinking {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.dot {
  width: 8px;
  height: 8px;
  background: #909399;
  border-radius: 50%;
  animation: blink 1.4s infinite both;
}

.dot:nth-child(2) {
  animation-delay: 0.2s;
}

.dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes blink {
  0%, 80%, 100% {
    opacity: 0.3;
  }

  40% {
    opacity: 1;
  }
}
</style>