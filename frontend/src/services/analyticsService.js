import api from './api'

const analyticsService = {
  async getAdherenceStats(params = {}) {
    const response = await api.get('/api/logs/stats/adherence', { params })
    return response.data
  },

  async getUsageTimeline(params = {}) {
    const response = await api.get('/api/logs/stats/usage-timeline', { params })
    return response.data
  },
}

export default analyticsService
