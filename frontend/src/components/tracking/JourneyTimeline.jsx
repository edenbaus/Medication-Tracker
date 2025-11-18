import { useState, useEffect } from 'react'
import journeyService from '../../services/journeyService'
import { thirdPartyService } from '../../services/thirdPartyService'
import { formatEasternDateTime, formatEasternDate } from '../../utils/dateUtils'
import './JourneyTimeline.css'

function JourneyTimeline({ days = 90 }) {
  const [journeyData, setJourneyData] = useState(null)
  const [thirdParties, setThirdParties] = useState([])
  const [selectedPerson, setSelectedPerson] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [activeView, setActiveView] = useState('timeline') // timeline, correlations, medications

  useEffect(() => {
    fetchThirdParties()
  }, [])

  useEffect(() => {
    if (thirdParties !== null) {
      fetchJourneyData()
    }
  }, [selectedPerson, days])

  const fetchThirdParties = async () => {
    try {
      const data = await thirdPartyService.getThirdParties()
      setThirdParties(data || [])
    } catch (err) {
      console.error('Failed to fetch third parties:', err)
    }
  }

  const fetchJourneyData = async () => {
    try {
      setLoading(true)
      setError('')

      const params = { days }
      if (selectedPerson) {
        params.third_party_id = selectedPerson
      }

      const data = await journeyService.getJourneyTimeline(params)
      setJourneyData(data)
    } catch (err) {
      console.error('Failed to fetch journey data:', err)
      setError('Failed to load journey timeline')
    } finally {
      setLoading(false)
    }
  }

  const getEventIcon = (eventType) => {
    switch (eventType) {
      case 'medication_start':
        return '💊'
      case 'log':
        return '✓'
      case 'side_effect':
        return '⚠️'
      case 'symptom':
        return '📊'
      default:
        return '•'
    }
  }

  const getEventClass = (eventType) => {
    switch (eventType) {
      case 'medication_start':
        return 'event-medication'
      case 'log':
        return 'event-log'
      case 'side_effect':
        return 'event-side-effect'
      case 'symptom':
        return 'event-symptom'
      default:
        return ''
    }
  }

  const getSeverityClass = (severity) => {
    if (!severity) return ''
    return `severity-${severity}`
  }

  if (loading) {
    return <div className="journey-timeline loading">Loading journey data...</div>
  }

  if (error) {
    return <div className="journey-timeline error">{error}</div>
  }

  if (!journeyData) {
    return <div className="journey-timeline empty">No journey data available.</div>
  }

  return (
    <div className="journey-timeline-container">
      {/* Header with person selector */}
      <div className="journey-header">
        <div className="journey-title">
          <h2>Medication Journey: {journeyData.person_name}</h2>
          <p className="journey-period">
            {formatEasternDate(new Date(journeyData.period_start))} -{' '}
            {formatEasternDate(new Date(journeyData.period_end))}
          </p>
        </div>

        <div className="journey-controls">
          <div className="control-group">
            <label>Person:</label>
            <select value={selectedPerson || ''} onChange={(e) => setSelectedPerson(e.target.value || null)}>
              <option value="">Me</option>
              {thirdParties.map((tp) => (
                <option key={tp.id} value={tp.id}>
                  {tp.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Summary stats */}
      <div className="journey-stats">
        <div className="stat-card">
          <div className="stat-value">{journeyData.total_medications}</div>
          <div className="stat-label">Medications</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{journeyData.total_logs}</div>
          <div className="stat-label">Doses Logged</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{journeyData.total_side_effects}</div>
          <div className="stat-label">Side Effects</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{journeyData.total_symptoms_tracked}</div>
          <div className="stat-label">Symptoms Tracked</div>
        </div>
      </div>

      {/* View tabs */}
      <div className="journey-tabs">
        <button
          className={`tab ${activeView === 'timeline' ? 'active' : ''}`}
          onClick={() => setActiveView('timeline')}
        >
          Timeline
        </button>
        <button
          className={`tab ${activeView === 'correlations' ? 'active' : ''}`}
          onClick={() => setActiveView('correlations')}
        >
          Symptom-Med Correlations
        </button>
        <button
          className={`tab ${activeView === 'medications' ? 'active' : ''}`}
          onClick={() => setActiveView('medications')}
        >
          Medication Details
        </button>
      </div>

      {/* Timeline View */}
      {activeView === 'timeline' && (
        <div className="timeline-view">
          <div className="timeline-legend">
            <div className="legend-item">
              <span className="legend-icon">💊</span> Medication Started
            </div>
            <div className="legend-item">
              <span className="legend-icon">✓</span> Dose Logged
            </div>
            <div className="legend-item">
              <span className="legend-icon">⚠️</span> Side Effect
            </div>
            <div className="legend-item">
              <span className="legend-icon">📊</span> Symptom Tracked
            </div>
          </div>

          <div className="timeline">
            {journeyData.events.length === 0 ? (
              <div className="empty-state">
                <p>No events in this time period.</p>
                <p>Start logging medications, tracking symptoms, or reporting side effects!</p>
              </div>
            ) : (
              journeyData.events.map((event) => (
                <div key={`${event.event_type}-${event.id}`} className={`timeline-event ${getEventClass(event.event_type)}`}>
                  <div className="event-icon">{getEventIcon(event.event_type)}</div>
                  <div className="event-content">
                    <div className="event-header">
                      <span className="event-time">{formatEasternDateTime(new Date(event.timestamp))}</span>
                      {event.medication_name && (
                        <span className="event-medication-badge">{event.medication_name}</span>
                      )}
                    </div>
                    <div className="event-description">
                      {event.description}
                      {event.severity && (
                        <span className={`severity-badge ${getSeverityClass(event.severity)}`}>
                          {event.severity}
                        </span>
                      )}
                      {event.improvement_level !== null && event.improvement_level !== undefined && (
                        <span className="improvement-badge">
                          Improvement: {event.improvement_level}/10
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Correlations View */}
      {activeView === 'correlations' && (
        <div className="correlations-view">
          <h3>Which Medications Treat Which Symptoms?</h3>

          {journeyData.symptom_medication_correlations.length === 0 ? (
            <div className="empty-state">
              <p>No symptom data available yet.</p>
              <p>Start tracking symptoms to see correlations with medications!</p>
            </div>
          ) : (
            <div className="correlation-cards">
              {journeyData.symptom_medication_correlations.map((corr, idx) => (
                <div key={idx} className="correlation-card">
                  <div className="correlation-header">
                    <h4>{corr.symptom_name}</h4>
                    <span className={`trend-badge trend-${corr.trend}`}>
                      {corr.trend === 'improving' && '📈 Improving'}
                      {corr.trend === 'stable' && '→ Stable'}
                      {corr.trend === 'worsening' && '📉 Worsening'}
                      {corr.trend === 'insufficient_data' && '📊 Insufficient Data'}
                    </span>
                  </div>

                  <div className="correlation-stats">
                    <div className="stat">
                      <strong>Average Improvement:</strong> {corr.average_improvement}/10
                    </div>
                  </div>

                  <div className="medications-list">
                    <strong>Treated by:</strong>
                    {corr.medications.map((med, medIdx) => (
                      <div key={medIdx} className="medication-treatment">
                        <span className="med-name">{med.medication_name}</span>
                        <span className="med-improvement">
                          Avg: {med.average_improvement}/10
                        </span>
                        <span className={`med-trend trend-${med.trend}`}>
                          ({med.trend})
                        </span>
                        <span className="med-data-points">
                          {med.data_points} data points
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Medications View */}
      {activeView === 'medications' && (
        <div className="medications-view">
          <h3>Medication Details & Side Effects</h3>

          {journeyData.medications.length === 0 ? (
            <div className="empty-state">
              <p>No medications in this time period.</p>
            </div>
          ) : (
            <div className="medication-journey-cards">
              {journeyData.medications.map((med) => {
                const sideEffectData = journeyData.medication_side_effect_correlations.find(
                  (se) => se.medication_id === med.medication_id
                )

                return (
                  <div key={med.medication_id} className="medication-journey-card">
                    <div className="med-journey-header">
                      <div>
                        <h4 style={{ color: med.color }}>{med.medication_name}</h4>
                        <p className="med-dates">
                          Started: {formatEasternDate(new Date(med.start_date))}
                          {med.end_date && ` • Ended: ${formatEasternDate(new Date(med.end_date))}`}
                          {!med.is_active && ' • Inactive'}
                        </p>
                      </div>
                      <div className="med-color-indicator" style={{ backgroundColor: med.color }}></div>
                    </div>

                    <div className="med-journey-stats">
                      <div className="stat">
                        <strong>{med.logs_count}</strong> doses logged
                      </div>
                      <div className="stat">
                        <strong>{med.symptoms_treated.length}</strong> symptoms tracked
                      </div>
                      <div className="stat">
                        <strong>{med.side_effects.length}</strong> side effects reported
                      </div>
                    </div>

                    {med.symptoms_treated.length > 0 && (
                      <div className="med-symptoms">
                        <strong>Symptoms Treated:</strong>
                        <div className="symptoms-grid">
                          {med.symptoms_treated.map((symptom, idx) => (
                            <div key={idx} className="symptom-item">
                              {symptom.symptom_name} ({symptom.improvement_level}/10)
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {sideEffectData && sideEffectData.side_effect_count > 0 && (
                      <div className="med-side-effects">
                        <strong>Side Effects ({sideEffectData.side_effect_count}):</strong>
                        <div className="severity-breakdown">
                          {sideEffectData.severity_distribution.mild > 0 && (
                            <span className="severity-count mild">
                              {sideEffectData.severity_distribution.mild} Mild
                            </span>
                          )}
                          {sideEffectData.severity_distribution.moderate > 0 && (
                            <span className="severity-count moderate">
                              {sideEffectData.severity_distribution.moderate} Moderate
                            </span>
                          )}
                          {sideEffectData.severity_distribution.severe > 0 && (
                            <span className="severity-count severe">
                              {sideEffectData.severity_distribution.severe} Severe
                            </span>
                          )}
                        </div>

                        <div className="side-effects-list">
                          {sideEffectData.side_effects.slice(0, 3).map((se, idx) => (
                            <div key={idx} className={`side-effect-item ${getSeverityClass(se.severity)}`}>
                              <span className="se-severity">{se.severity}:</span>
                              <span className="se-description">{se.description}</span>
                            </div>
                          ))}
                          {sideEffectData.side_effects.length > 3 && (
                            <div className="more-indicator">
                              +{sideEffectData.side_effects.length - 3} more
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default JourneyTimeline
