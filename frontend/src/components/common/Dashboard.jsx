import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import authService from '../../services/authService'
import dashboardService from '../../services/dashboardService'
import { formatEasternDateTime, formatEasternDate } from '../../utils/dateUtils'
import './Dashboard.css'

function Dashboard() {
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedPerson, setSelectedPerson] = useState(null) // null means "Me"
  const navigate = useNavigate()

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Check for token before making any API calls
        if (!authService.isAuthenticated()) {
          console.log('[Dashboard] No token found, redirecting to login')
          navigate('/login')
          return
        }

        console.log('[Dashboard] Token found, fetching dashboard data')
        const data = await dashboardService.getDashboardSummary()
        setDashboardData(data)
        console.log('[Dashboard] Dashboard data loaded')
      } catch (error) {
        console.error('[Dashboard] Failed to fetch data:', error)
        // Only navigate to login if it's truly an auth error
        if (error.response?.status === 401) {
          console.log('[Dashboard] 401 error, clearing token and redirecting')
          localStorage.removeItem('access_token')
          navigate('/login')
        } else {
          setError('Failed to load dashboard data')
        }
      } finally {
        setLoading(false)
      }
    }

    // Small delay to ensure token is set from OAuth callback
    const timer = setTimeout(() => {
      fetchData()
    }, 100)

    return () => clearTimeout(timer)
  }, [navigate])

  const getActivityIcon = (activityType) => {
    switch (activityType) {
      case 'log':
        return '✓'
      case 'side_effect':
        return '⚠️'
      case 'symptom':
        return '📊'
      case 'medication_added':
        return '💊'
      default:
        return '•'
    }
  }

  const getActivityClass = (activityType) => {
    switch (activityType) {
      case 'log':
        return 'activity-log'
      case 'side_effect':
        return 'activity-side-effect'
      case 'symptom':
        return 'activity-symptom'
      case 'medication_added':
        return 'activity-medication'
      default:
        return ''
    }
  }

  if (loading) {
    return (
      <div className="container dashboard-loading">
        <p>Loading your dashboard...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container dashboard-error">
        <p className="error-message">{error}</p>
        <button onClick={() => window.location.reload()} className="btn btn-primary">
          Try Again
        </button>
      </div>
    )
  }

  if (!dashboardData) {
    return null
  }

  // Get stats for the selected person (or current user if no selection)
  const currentPersonStats = selectedPerson
    ? dashboardData.people_stats.find(p => p.person_id === selectedPerson)
    : dashboardData.people_stats.find(p => p.person_id === null) // "Me"

  const currentPersonName = currentPersonStats ? currentPersonStats.person_name : 'Me'

  // Filter activities and alerts for selected person
  const filteredActivities = selectedPerson !== null
    ? dashboardData.recent_activity.filter(a => a.person_id === selectedPerson)
    : dashboardData.recent_activity.filter(a => a.person_id === null)

  const filteredMedsNeedingAttention = selectedPerson !== null
    ? dashboardData.medications_needing_attention.filter(m => m.person_id === selectedPerson)
    : dashboardData.medications_needing_attention.filter(m => m.person_id === null)

  const filteredRefillAlerts = selectedPerson !== null
    ? (dashboardData.refill_alerts || []).filter(r => r.person_id === selectedPerson)
    : (dashboardData.refill_alerts || []).filter(r => r.person_id === null)

  return (
    <div className="container dashboard">
      {/* Welcome Header */}
      <div className="dashboard-header">
        <h1>Welcome back, {dashboardData.user_name}!</h1>
        <p className="dashboard-subtitle">Here's your medication tracking overview</p>
      </div>

      {/* Person Selector */}
      {dashboardData.people_stats && dashboardData.people_stats.length > 1 && (
        <div className="person-selector-section">
          <label htmlFor="person-select" className="person-selector-label">
            Viewing data for:
          </label>
          <div className="person-selector-buttons">
            {dashboardData.people_stats.map((person) => (
              <button
                key={person.person_id || 'me'}
                className={`person-selector-btn ${selectedPerson === person.person_id ? 'active' : ''}`}
                onClick={() => setSelectedPerson(person.person_id)}
              >
                {person.person_name}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Quick Stats - Now showing individual person data */}
      <div className="stats-grid">
        <div className="stat-card stat-medications">
          <div className="stat-icon">💊</div>
          <div className="stat-content">
            <div className="stat-value">{currentPersonStats?.active_medications || 0}</div>
            <div className="stat-label">Active Medications</div>
          </div>
        </div>

        <div className="stat-card stat-logs-today">
          <div className="stat-icon">✓</div>
          <div className="stat-content">
            <div className="stat-value">
              {selectedPerson === null
                ? dashboardData.total_logs_today
                : currentPersonStats?.total_logs_7days || 0}
            </div>
            <div className="stat-label">{selectedPerson === null ? 'Doses Today' : 'Doses (7 days)'}</div>
          </div>
        </div>

        <div className="stat-card stat-logs-week">
          <div className="stat-icon">📅</div>
          <div className="stat-content">
            <div className="stat-value">{currentPersonStats?.total_logs_7days || 0}</div>
            <div className="stat-label">Doses This Week</div>
          </div>
        </div>

        <div className="stat-card stat-side-effects">
          <div className="stat-icon">⚠️</div>
          <div className="stat-content">
            <div className="stat-value">{currentPersonStats?.side_effects_7days || 0}</div>
            <div className="stat-label">Side Effects (7 days)</div>
          </div>
        </div>

        <div className="stat-card stat-symptoms">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <div className="stat-value">{currentPersonStats?.symptoms_tracked_7days || 0}</div>
            <div className="stat-label">Symptoms Tracked (7 days)</div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions-section">
        <h2>Quick Actions</h2>
        <div className="quick-actions-grid">
          <Link to="/medications" className="quick-action-card action-medications">
            <div className="action-icon">💊</div>
            <div className="action-label">Manage Medications</div>
            <div className="action-description">Add, edit, or view medications</div>
          </Link>

          <Link to="/logs" className="quick-action-card action-logs">
            <div className="action-icon">✓</div>
            <div className="action-label">Log a Dose</div>
            <div className="action-description">Record medication taken</div>
          </Link>

          <Link to="/tracking" className="quick-action-card action-tracking">
            <div className="action-icon">📈</div>
            <div className="action-label">View Analytics</div>
            <div className="action-description">Track trends and journey</div>
          </Link>

          <Link to="/regimens" className="quick-action-card action-regimens">
            <div className="action-icon">⏰</div>
            <div className="action-label">Manage Regimens</div>
            <div className="action-description">Set up medication schedules</div>
          </Link>
        </div>
      </div>

      {/* Per-Person Stats */}
      {dashboardData.people_stats && dashboardData.people_stats.length > 1 && (
        <div className="people-stats-section">
          <h2>People Overview</h2>
          <div className="people-stats-grid">
            {dashboardData.people_stats.map((person, idx) => (
              <div key={idx} className="person-stat-card">
                <h3 className="person-name">{person.person_name}</h3>
                <div className="person-stats">
                  <div className="person-stat">
                    <span className="person-stat-value">{person.active_medications}</span>
                    <span className="person-stat-label">Active Meds</span>
                  </div>
                  <div className="person-stat">
                    <span className="person-stat-value">{person.total_logs_7days}</span>
                    <span className="person-stat-label">Doses (7d)</span>
                  </div>
                  <div className="person-stat">
                    <span className="person-stat-value">{person.side_effects_7days}</span>
                    <span className="person-stat-label">Side Effects</span>
                  </div>
                  <div className="person-stat">
                    <span className="person-stat-value">{person.symptoms_tracked_7days}</span>
                    <span className="person-stat-label">Symptoms</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Refill Alerts */}
      {filteredRefillAlerts && filteredRefillAlerts.length > 0 && (
        <div className="attention-section">
          <h2>🔔 Prescription Refills Due</h2>
          <p className="section-subtitle">These medications need to be refilled soon</p>
          <div className="attention-list">
            {filteredRefillAlerts.slice(0, 5).map((alert) => (
              <div key={alert.medication_id} className="attention-card refill-alert-card">
                <div className="attention-header">
                  <h4>{alert.medication_name}</h4>
                  <span className="attention-person">{alert.person_name}</span>
                </div>
                <div className="attention-details">
                  <p className="attention-time">
                    Refill date: {alert.refill_date ? formatEasternDate(new Date(alert.refill_date)) : 'N/A'}
                  </p>
                  <p className={`attention-warning ${alert.days_until_refill < 0 ? 'overdue' : ''}`}>
                    {alert.days_until_refill < 0
                      ? `Overdue by ${Math.abs(alert.days_until_refill)} day${Math.abs(alert.days_until_refill) !== 1 ? 's' : ''}`
                      : `Due in ${alert.days_until_refill} day${alert.days_until_refill !== 1 ? 's' : ''}`}
                  </p>
                  <p className="refill-remaining">
                    {alert.refills_remaining} refill{alert.refills_remaining !== 1 ? 's' : ''} remaining
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Medications Needing Attention */}
      {filteredMedsNeedingAttention && filteredMedsNeedingAttention.length > 0 && (
        <div className="attention-section">
          <h2>⚠️ Medications Needing Attention</h2>
          <p className="section-subtitle">These medications haven't been logged recently for {currentPersonName}</p>
          <div className="attention-list">
            {filteredMedsNeedingAttention.slice(0, 5).map((med) => (
              <div key={med.medication_id} className="attention-card">
                <div className="attention-header">
                  <h4>{med.medication_name}</h4>
                  <span className="attention-person">{med.person_name}</span>
                </div>
                <div className="attention-details">
                  {med.last_logged ? (
                    <>
                      <p className="attention-time">
                        Last logged: {formatEasternDate(new Date(med.last_logged))}
                      </p>
                      <p className="attention-warning">
                        {med.days_since_last_log} day{med.days_since_last_log !== 1 ? 's' : ''} ago
                      </p>
                    </>
                  ) : (
                    <p className="attention-warning">Never logged</p>
                  )}
                </div>
                <Link to="/logs" className="btn btn-sm btn-primary">
                  Log Now
                </Link>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Activity */}
      {filteredActivities && filteredActivities.length > 0 && (
        <div className="recent-activity-section">
          <h2>Recent Activity for {currentPersonName}</h2>
          <div className="activity-timeline">
            {filteredActivities.map((activity) => (
              <div key={`${activity.activity_type}-${activity.id}`} className={`activity-item ${getActivityClass(activity.activity_type)}`}>
                <div className="activity-icon">{getActivityIcon(activity.activity_type)}</div>
                <div className="activity-content">
                  <div className="activity-header">
                    <span className="activity-time">
                      {formatEasternDateTime(new Date(activity.timestamp))}
                    </span>
                    <span className="activity-person">{activity.person_name}</span>
                  </div>
                  <p className="activity-description">
                    {activity.description}
                    {activity.severity && (
                      <span className={`severity-badge severity-${activity.severity}`}>
                        {activity.severity}
                      </span>
                    )}
                  </p>
                  {activity.medication_name && (
                    <span className="activity-medication-badge">{activity.medication_name}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
