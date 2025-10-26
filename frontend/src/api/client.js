import axios from 'axios'
import * as Sentry from '@sentry/browser'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  // If sending FormData, let the browser set Content-Type
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type']
  }
  return config
})

// Handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    const url = error.config?.url || ''
    if (status >= 500 && (url.includes('/auth') || url.includes('/analyze') || url.includes('/ocr'))) {
      Sentry.captureException(error, {
        tags: { area: 'api', status },
        extra: { url, data: error.response?.data },
      })
    }
    if (status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    } else if (status === 402) {
      // Token exhausted – emit a custom event for modal handling
      const evt = new CustomEvent('billing:upgrade_required', { detail: { reason: 'tokens_exhausted' } })
      window.dispatchEvent(evt)
    } else if (status === 429) {
      const retryAfter = error.response?.data?.retry_after ?? 60
      const evt = new CustomEvent('rate:limited', { detail: { retryAfter } })
      window.dispatchEvent(evt)
    }
    return Promise.reject(error)
  }
)

export default apiClient

