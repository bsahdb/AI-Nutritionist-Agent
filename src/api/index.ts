import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export interface StandardResponse<T = any> {
  success: boolean
  message: string
  data: T
}

export interface HealthReport {
  id: number
  user_id: number
  report_name?: string
  fasting_glucose?: number
  postprandial_glucose?: number
  total_cholesterol?: number
  triglycerides?: number
  hdl_cholesterol?: number
  ldl_cholesterol?: number
  systolic_bp?: number
  diastolic_bp?: number
  uric_acid?: number
  creatinine?: number
  bun?: number
  alt?: number
  ast?: number
  hemoglobin?: number
  notes?: string
  created_at?: string
}

export interface HealthReportForm {
  user_id?: number
  report_name?: string
  fasting_glucose?: number | null
  postprandial_glucose?: number | null
  total_cholesterol?: number | null
  triglycerides?: number | null
  hdl_cholesterol?: number | null
  ldl_cholesterol?: number | null
  systolic_bp?: number | null
  diastolic_bp?: number | null
  uric_acid?: number | null
  creatinine?: number | null
  bun?: number | null
  alt?: number | null
  ast?: number | null
  hemoglobin?: number | null
  notes?: string
}

// 用户管理
// 用户管理
export async function listUsers() {
  return (await api.get('/users/')).data
}

export async function createUser(data: any) {
  return (await api.post('/users/', data)).data
}

export async function getUser(userId: number) {
  return (await api.get(`/users/${userId}`)).data
}

export async function updateUser(userId: number, data: any) {
  return (await api.put(`/users/${userId}`, data)).data
}

export async function deleteUser(userId: number) {
  return (await api.delete(`/users/${userId}`)).data
}

// 体检报告
export async function getHealthReports(userId: number) {
  return (await api.get<StandardResponse<HealthReport[]>>('/health/reports', {
    params: {
      user_id: userId
    }
  })).data
}

export async function getHealthReportDetail(reportId: number) {
  return (await api.get<StandardResponse<HealthReport>>(`/health/reports/${reportId}`)).data
}

export async function createHealthReport(userId: number, data: HealthReportForm) {
  return (await api.post<StandardResponse<HealthReport>>('/health/reports', {
    user_id: userId,
    ...data
  })).data
}

export async function updateHealthReport(reportId: number, data: Partial<HealthReportForm>) {
  return (await api.put<StandardResponse<HealthReport>>(`/health/reports/${reportId}`, data)).data
}

export async function deleteHealthReport(reportId: number) {
  return (await api.delete<StandardResponse>(`/health/reports/${reportId}`)).data
}

export async function analyzeHealth(userId: number, reportId: number) {
  return (await api.post<StandardResponse<{
    data_source: any
    analysis: string
  }>>('/health/analyze', {
    user_id: userId,
    report_id: reportId
  })).data
}

// 兼容 HealthReport.vue 里原来的 healthApi 写法
export const healthApi = {
  getReports(userId = 1) {
    return api.get<StandardResponse<HealthReport[]>>('/health/reports', {
      params: { user_id: userId }
    })
  },

  createReport(data: HealthReportForm & { user_id: number }) {
    return api.post<StandardResponse<HealthReport>>('/health/reports', data)
  },

  updateReport(reportId: number, data: Partial<HealthReportForm>) {
    return api.put<StandardResponse<HealthReport>>(`/health/reports/${reportId}`, data)
  },

  deleteReport(reportId: number) {
    return api.delete<StandardResponse>(`/health/reports/${reportId}`)
  },

  analyzeHealth(userId: number, reportId: number) {
    return api.post<StandardResponse<{
      data_source: any
      analysis: string
    }>>('/health/analyze', {
      user_id: userId,
      report_id: reportId
    })
  }
}

// 口味偏好：多记录版本
export async function listPreferencesByUser(userId: number) {
  return (await api.get(`/preferences/user/${userId}`)).data
}

export async function getPreferenceDetail(prefId: number) {
  return (await api.get(`/preferences/detail/${prefId}`)).data
}

// 兼容旧逻辑：获取当前用户默认偏好
export async function getPreferences(userId: number) {
  return (await api.get(`/preferences/${userId}`)).data
}

export async function createPreferences(userId: number, data: any) {
  return (await api.post('/preferences/', {
    user_id: userId,
    ...data
  })).data
}

export async function updatePreferenceById(prefId: number, data: any) {
  return (await api.put(`/preferences/detail/${prefId}`, data)).data
}

export async function deletePreference(prefId: number) {
  return (await api.delete(`/preferences/detail/${prefId}`)).data
}

export async function setDefaultPreference(prefId: number) {
  return (await api.put(`/preferences/default/${prefId}`)).data
}

// 兼容旧页面/Store：保存默认偏好
export async function savePreferences(userId: number, data: any) {
  try {
    return (await api.put(`/preferences/${userId}`, data)).data
  } catch (error: any) {
    if (error?.response?.status === 404) {
      return await createPreferences(userId, {
        ...data,
        preference_name: data.preference_name || '默认偏好',
        is_default: 1
      })
    }

    throw error
  }
}

// 饮食计划
export async function generateMealPlan(data: {
  user_id: number
  report_id: number
  days: number
  meal_count: number
  target_calories?: number | null
  requirements?: string
  title?: string
}) {
  return (await api.post('/meal-plans/generate', data)).data
}

export async function listMealPlans(userId: number) {
  return (await api.get('/meal-plans', {
    params: {
      user_id: userId
    }
  })).data
}

export async function getMealPlanDetail(planId: number) {
  return (await api.get(`/meal-plans/${planId}`)).data
}

export async function deleteMealPlan(planId: number) {
  return (await api.delete(`/meal-plans/${planId}`)).data
}

// AI Agent 对话
export async function agentChat(
  userId: number,
  message: string,
  reportId?: number,
  context?: any
) {
  return (await api.post('/agent/chat', {
    user_id: userId,
    message,
    context: {
      ...(context || {}),
      report_id: reportId
    }
  })).data
}

// 数据看板
export async function getDashboardSummary(userId?: number) {
  return (await api.get('/dashboard/summary', {
    params: userId ? { user_id: userId } : {}
  })).data
}

export default api