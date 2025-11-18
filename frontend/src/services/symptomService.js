import api from './api'

const symptomService = {
  async getSymptoms(params = {}) {
    const response = await api.get('/api/symptoms', { params })
    return response.data
  },

  async createSymptom(data) {
    const response = await api.post('/api/symptoms', data)
    return response.data
  },

  async getSymptom(id) {
    const response = await api.get(`/api/symptoms/${id}`)
    return response.data
  },

  async updateSymptom(id, data) {
    const response = await api.put(`/api/symptoms/${id}`, data)
    return response.data
  },

  async deleteSymptom(id) {
    await api.delete(`/api/symptoms/${id}`)
  },

  async getSymptomTrends(params = {}) {
    const response = await api.get('/api/symptoms/trends', { params })
    return response.data
  },

  async getSymptomWithImages(id) {
    const response = await api.get(`/api/symptoms/${id}/with-images`)
    return response.data
  },

  async uploadSymptomImages(symptomId, files) {
    const formData = new FormData()
    files.forEach(file => {
      formData.append('files', file)
    })

    const response = await api.post(
      `/api/symptoms/${symptomId}/images`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  },

  async deleteSymptomImage(symptomId, imageId) {
    await api.delete(`/api/symptoms/${symptomId}/images/${imageId}`)
  },

  getImageUrl(imagePath) {
    // Convert file path to URL
    // Example: /app/uploads/symptom-id/filename.jpg -> http://localhost:8000/uploads/symptom-id/filename.jpg
    const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    const path = imagePath.replace('/app', '')
    return `${baseURL}${path}`
  },
}

export default symptomService
