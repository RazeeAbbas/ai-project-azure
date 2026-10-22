import axios from 'axios'

// API base URL from environment variable (never hardcoded)
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor – add correlation ID
api.interceptors.request.use((config) => {
  config.headers['X-Request-ID'] = crypto.randomUUID().slice(0, 8)
  return config
})

// Response interceptor – normalize errors
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const message =
      err.response?.data?.detail ||
      err.response?.data?.message ||
      err.message ||
      'Unknown error'
    return Promise.reject(new Error(message))
  }
)

export default api

