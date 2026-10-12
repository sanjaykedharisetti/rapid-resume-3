/**
 * Centralized API service using Axios.
 * All backend communication goes through this module.
 * The base URL is read from VITE_API_BASE_URL env var.
 */
import axios from 'axios'

const envUrl = (import.meta.env.VITE_API_BASE_URL || '').trim()
const _rawUrl = envUrl || (import.meta.env.PROD ? 'https://rapid-resume-3-1.onrender.com' : '')
// Render passes just the hostname (e.g. "rapid-resume-backend.onrender.com")
// so we need to add https:// if it doesn't already have a protocol
const BASE_URL = _rawUrl && !_rawUrl.startsWith('http')
  ? `https://${_rawUrl}`
  : _rawUrl

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 120000, // 2 minutes (NLP model may be slow on cold start)
})

// Response interceptor: normalize errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNABORTED') {
      return Promise.reject({
        message: 'Request timed out. The server may be starting up. Please try again.',
        code: 'TIMEOUT',
      })
    }
    if (!error.response) {
      return Promise.reject({
        message: 'Cannot reach the backend server. Please ensure it is running.',
        code: 'NETWORK_ERROR',
      })
    }
    const detail = error.response.data?.detail || error.response.statusText || 'Unknown error'
    return Promise.reject({
      message: detail,
      status: error.response.status,
      code: `HTTP_${error.response.status}`,
    })
  }
)

// ── Health ─────────────────────────────────────────────────────────────────

export const checkHealth = () => api.get('/api/health').then((r) => r.data)

export const checkReadiness = () => api.get('/api/health/ready').then((r) => r.data)

// ── Analysis ───────────────────────────────────────────────────────────────

/**
 * Analyze a resume against a job description.
 * @param {File} resumeFile - The resume file (PDF or DOCX)
 * @param {string} jobDescription - The job description text
 * @param {function} onUploadProgress - Progress callback
 */
export const analyzeResume = (resumeFile, jobDescription, onUploadProgress) => {
  const formData = new FormData()
  formData.append('resume', resumeFile)
  formData.append('job_description', jobDescription)

  return api
    .post('/api/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress,
    })
    .then((r) => r.data)
}

// ── History ────────────────────────────────────────────────────────────────

export const getHistory = () => api.get('/api/history').then((r) => r.data)

export const getHistoryDetail = (id) =>
  api.get(`/api/history/${id}`).then((r) => r.data)

export const deleteHistory = (id) => api.delete(`/api/history/${id}`)

export const getReportUrl = (id) => `${BASE_URL}/api/history/${id}/report`

// ── AI Resume Optimization ─────────────────────────────────────────────────

/**
 * Optimize resume with AI.
 * @param {string} analysisId - ID of previous analysis record
 * @param {object} options - { target_score, iterations }
 */
export const optimizeResume = (analysisId, options = {}) =>
  api
    .post('/api/optimize', {
      analysis_id: analysisId,
      target_score: options.target_score || 85.0,
      iterations: options.iterations || 3,
    })
    .then((r) => r.data)

export const getOptimization = (analysisId) =>
  api.get(`/api/optimize/${analysisId}`).then((r) => r.data)

export const getOptimizedPdfUrl = (analysisId) =>
  `${BASE_URL}/api/optimize/${analysisId}/pdf`

export const getOptimizedReportUrl = (analysisId) =>
  `${BASE_URL}/api/optimize/${analysisId}/report`

export const getOptimizedDocxUrl = (analysisId) =>
  `${BASE_URL}/api/optimize/${analysisId}/docx`

export default api

