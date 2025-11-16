import api from './api'

const authService = {
  async register(userData) {
    const response = await api.post('/api/auth/register', userData)
    return response.data
  },

  async login(email, password) {
    const formData = new URLSearchParams()
    formData.append('username', email) // OAuth2 uses 'username' field
    formData.append('password', password)

    const response = await api.post('/api/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })

    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token)
    }

    return response.data
  },

  async getCurrentUser() {
    const response = await api.get('/api/auth/me')
    return response.data
  },

  logout() {
    localStorage.removeItem('access_token')
  },

  isAuthenticated() {
    return !!localStorage.getItem('access_token')
  },
}

export default authService
