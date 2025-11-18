import api from './api'

const dashboardService = {
  async getDashboardSummary() {
    const response = await api.get('/api/dashboard/summary')
    return response.data
  },
}

export default dashboardService
