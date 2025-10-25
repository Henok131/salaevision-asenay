import apiClient from './client'

export const analysisAPI = {
  // Upload and analyze sales data
  analyzeData: async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    
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
    const response = await apiClient.get('/analysis/history/')
    return response.data
  }
}

