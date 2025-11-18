import api from './api'

const medicationService = {
  // Get all medications
  async getMedications(params = {}) {
    const queryString = new URLSearchParams(params).toString()
    const url = queryString ? `/api/medications/?${queryString}` : '/api/medications/'
    const response = await api.get(url)
    return response.data
  },

  // Get single medication
  async getMedication(id) {
    const response = await api.get(`/api/medications/${id}`)
    return response.data
  },

  // Create medication
  async createMedication(data) {
    const response = await api.post('/api/medications/', data)
    return response.data
  },

  // Update medication
  async updateMedication(id, data) {
    const response = await api.put(`/api/medications/${id}`, data)
    return response.data
  },

  // Delete medication
  async deleteMedication(id) {
    const response = await api.delete(`/api/medications/${id}`)
    return response.data
  },

  // Get all tags
  async getTags() {
    const response = await api.get('/api/tags/')
    return response.data
  },

  // Create tag
  async createTag(data) {
    const response = await api.post('/api/tags/', data)
    return response.data
  },

  // Add tag to medication
  async addTagToMedication(medicationId, tagId) {
    const response = await api.post(`/api/medications/${medicationId}/tags/${tagId}`)
    return response.data
  },

  // Remove tag from medication
  async removeTagFromMedication(medicationId, tagId) {
    const response = await api.delete(`/api/medications/${medicationId}/tags/${tagId}`)
    return response.data
  },
}

export default medicationService
