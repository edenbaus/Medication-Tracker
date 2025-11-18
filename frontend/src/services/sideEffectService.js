import api from './api'

const sideEffectService = {
  async getSideEffects(params = {}) {
    const response = await api.get('/api/side-effects', { params })
    return response.data
  },

  async createSideEffect(data) {
    const response = await api.post('/api/side-effects', data)
    return response.data
  },

  async getSideEffect(id) {
    const response = await api.get(`/api/side-effects/${id}`)
    return response.data
  },

  async updateSideEffect(id, data) {
    const response = await api.put(`/api/side-effects/${id}`, data)
    return response.data
  },

  async deleteSideEffect(id) {
    await api.delete(`/api/side-effects/${id}`)
  },
}

export default sideEffectService
