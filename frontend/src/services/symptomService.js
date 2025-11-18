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
}

export default symptomService
