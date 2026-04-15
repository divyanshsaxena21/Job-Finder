import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL

if (!API_BASE_URL) {
  console.error('CRITICAL: VITE_API_URL environment variable is not set. API calls will fail.')
}

const api = axios.create({
  baseURL: API_BASE_URL,
})

// Attach JWT token to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const authAPI = {
  register: (name, email, password, telegramChatId) =>
    api.post('/auth/register', {
      name,
      email,
      password,
      telegram_chat_id: telegramChatId
    }),
  
  login: (email, password) =>
    api.post('/auth/login', {
      email,
      password
    }),
  
  getMe: () => api.get('/auth/me')
}

export const jobsAPI = {
  create: (jobData) => api.post('/jobs', jobData),
  getAll: (skip = 0, limit = 20) =>
    api.get('/jobs', { params: { skip, limit } }),
  getById: (jobId) => api.get(`/jobs/${jobId}`),
  matchJob: (jobId) => api.post(`/jobs/${jobId}/match`),
  generateResume: (jobId) => api.post(`/jobs/${jobId}/generate-resume`),
  generateCoverLetter: (jobId) => api.post(`/jobs/${jobId}/generate-cover-letter`),
  filterByPreferences: () => api.get('/jobs/filter-by-preferences')
}

export const applicationsAPI = {
  submit: (jobId, resume, coverLetter) =>
    api.post(`/applications/${jobId}/submit`, {
      resume,
      cover_letter: coverLetter
    }),
  getAll: (statusFilter = null) =>
    api.get('/applications', { params: { status_filter: statusFilter } }),
  getById: (appId) => api.get(`/applications/${appId}`),
  approve: (appId) => api.post(`/applications/${appId}/approve`),
  reject: (appId) => api.post(`/applications/${appId}/reject`)
}

export const preferencesAPI = {
  get: () => api.get('/preferences'),
  update: (preferences) => api.put('/preferences', preferences)
}

export default api
