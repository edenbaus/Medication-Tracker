import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import authService from '../../services/authService'

function Dashboard() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    const fetchUser = async () => {
      try {
        if (!authService.isAuthenticated()) {
          navigate('/login')
          return
        }

        const userData = await authService.getCurrentUser()
        setUser(userData)
      } catch (error) {
        console.error('Failed to fetch user:', error)
        navigate('/login')
      } finally {
        setLoading(false)
      }
    }

    fetchUser()
  }, [navigate])

  const handleLogout = () => {
    authService.logout()
    navigate('/login')
  }

  if (loading) {
    return (
      <div className="container">
        <p>Loading...</p>
      </div>
    )
  }

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h1>Medication Tracker Dashboard</h1>
        <button onClick={handleLogout} className="btn" style={{ width: 'auto', padding: '10px 20px' }}>
          Logout
        </button>
      </div>

      {user && (
        <div style={{ background: 'white', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
          <h2>Welcome, {user.username}!</h2>
          <p>Email: {user.email}</p>
        </div>
      )}

      <div style={{ background: 'white', padding: '20px', borderRadius: '8px' }}>
        <h3>Getting Started</h3>
        <p>Your medication tracker is now set up and ready to use.</p>
        <p>Features coming soon:</p>
        <ul>
          <li>Add and manage medications</li>
          <li>Log medication intake</li>
          <li>Track side effects and symptoms</li>
          <li>View analytics and reports</li>
          <li>Organize medications with tags</li>
        </ul>
      </div>
    </div>
  )
}

export default Dashboard
