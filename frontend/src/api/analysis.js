import apiClient from './client'

export const analysisAPI = {
  // Upload and analyze sales data (CSV + optional image + text)
  analyzeData: async (file, image, text) => {
    const formData = new FormData()
    if (file) formData.append('file', file)
    if (image) formData.append('image', image)
    if (typeof text === 'string' && text.length > 0) formData.append('text', text)

    const response = await apiClient.post('/analyze/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  // Generate forecast
  generateForecast: async (analysisId, days = 30) => {
    const response = await apiClient.post('/forecast/', {
      analysis_id: analysisId,
      days: days
    })
    return response.data
  },

  // Get explanations
  getExplanations: async (analysisId) => {
    const response = await apiClient.post('/explain/', {
      analysis_id: analysisId
    })
    return response.data
  },

  // Get analysis history
  getAnalysisHistory: async () => {
    const response = await apiClient.get('/analyze/history/')
    return response.data
  }
}

