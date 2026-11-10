import axios from 'axios'

// API base URL from environment variable (never hardcoded)
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const createRequestId = (): string => {
  if (typeof globalThis.crypto?.randomUUID === 'function') {
    return globalThis.crypto.randomUUID().slice(0, 8)
  }

  if (typeof globalThis.crypto?.getRandomValues === 'function') {
    return Array.from(globalThis.crypto.getRandomValues(new Uint8Array(4)), (value) =>
      value.toString(16).padStart(2, '0'),
    ).join('')
  }

  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`
}

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
  // NOTE: Do NOT set Content-Type here for multipart uploads.
  // Axios must set it automatically with the boundary parameter.
})

// Request interceptor – add correlation ID
api.interceptors.request.use((config) => {
  config.headers['X-Request-ID'] = createRequestId()
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

