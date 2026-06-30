import axios from 'axios'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  timeout: 120000
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
  user_id: number
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

export const healthApi = {
  getReports(userId = 1) {
    return http.get<StandardResponse<HealthReport[]>>('/health/reports', {
      params: { user_id: userId }
    })
  },

  createReport(data: HealthReportForm) {
    return http.post<StandardResponse<HealthReport>>('/health/reports', data)
  },

  updateReport(reportId: number, data: Partial<HealthReportForm>) {
    return http.put<StandardResponse<HealthReport>>(`/health/reports/${reportId}`, data)
  },

  deleteReport(reportId: number) {
    return http.delete<StandardResponse>(`/health/reports/${reportId}`)
  },

  analyzeHealth(userId: number, reportId: number) {
    return http.post<StandardResponse<{
      data_source: any
      analysis: string
    }>>('/health/analyze', {
      user_id: userId,
      report_id: reportId
    })
  }
}