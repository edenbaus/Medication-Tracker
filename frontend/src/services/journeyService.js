import api from './api'

const journeyService = {
  async getJourneyTimeline(params = {}) {
    const response = await api.get('/api/journey/timeline', { params })
    return response.data
  },
}

export default journeyService
