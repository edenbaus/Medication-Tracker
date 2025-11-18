import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import authService from '../../services/authService'
import TrendsChart from './TrendsChart'
import SideEffectForm from './SideEffectForm'
import SymptomTracker from './SymptomTracker'
import JourneyTimeline from './JourneyTimeline'
import sideEffectService from '../../services/sideEffectService'
import symptomService from '../../services/symptomService'
import { formatEasternDateTime } from '../../utils/dateUtils'
import './TrackingPage.css'

function TrackingPage() {
  const [activeTab, setActiveTab] = useState('chart')
  const [sideEffects, setSideEffects] = useState([])
  const [symptoms, setSymptoms] = useState([])
  const [loading, setLoading] = useState(true)
  const [showSideEffectForm, setShowSideEffectForm] = useState(false)
  const [showSymptomForm, setShowSymptomForm] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    if (!authService.isAuthenticated()) {
      navigate('/login')
      return
    }

    fetchData()
  }, [navigate])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [sideEffectsData, symptomsData] = await Promise.all([
        sideEffectService.getSideEffects({ limit: 10 }),
        symptomService.getSymptoms({ limit: 10 }),
      ])

      setSideEffects(sideEffectsData)
      setSymptoms(symptomsData)
    } catch (error) {
      console.error('Failed to fetch tracking data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSideEffectSuccess = () => {
    setShowSideEffectForm(false)
    fetchData()
  }

  const handleSymptomSuccess = () => {
    setShowSymptomForm(false)
    fetchData()
  }

  const handleDeleteSideEffect = async (id) => {
    if (!window.confirm('Are you sure you want to delete this side effect report?')) {
      return
    }

    try {
      await sideEffectService.deleteSideEffect(id)
      fetchData()
    } catch (error) {
      console.error('Failed to delete side effect:', error)
    }
  }

  const handleDeleteSymptom = async (id) => {
    if (!window.confirm('Are you sure you want to delete this symptom tracking entry?')) {
      return
    }

    try {
      await symptomService.deleteSymptom(id)
      fetchData()
    } catch (error) {
      console.error('Failed to delete symptom:', error)
    }
  }

  if (loading) {
    return <div className="container">Loading...</div>
  }

  return (
    <div className="container tracking-page">
      <h1>Medication Tracking & Analytics</h1>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'journey' ? 'active' : ''}`}
          onClick={() => setActiveTab('journey')}
        >
          Complete Journey
        </button>
        <button
          className={`tab ${activeTab === 'chart' ? 'active' : ''}`}
          onClick={() => setActiveTab('chart')}
        >
          Usage Chart
        </button>
        <button
          className={`tab ${activeTab === 'sideEffects' ? 'active' : ''}`}
          onClick={() => setActiveTab('sideEffects')}
        >
          Side Effects
        </button>
        <button
          className={`tab ${activeTab === 'symptoms' ? 'active' : ''}`}
          onClick={() => setActiveTab('symptoms')}
        >
          Symptom Tracking
        </button>
      </div>

      {activeTab === 'journey' && (
        <div className="tab-content">
          <JourneyTimeline days={90} />
        </div>
      )}

      {activeTab === 'chart' && (
        <div className="tab-content">
          <TrendsChart days={30} chartType="line" />
        </div>
      )}

      {activeTab === 'sideEffects' && (
        <div className="tab-content">
          <div className="section-header">
            <h2>Side Effects</h2>
            <button
              className="btn btn-primary"
              onClick={() => setShowSideEffectForm(!showSideEffectForm)}
            >
              {showSideEffectForm ? 'Cancel' : '+ Report Side Effect'}
            </button>
          </div>

          {showSideEffectForm && (
            <SideEffectForm
              onSuccess={handleSideEffectSuccess}
              onCancel={() => setShowSideEffectForm(false)}
            />
          )}

          <div className="tracking-list">
            {sideEffects.length === 0 ? (
              <div className="empty-state">
                <p>No side effects reported yet.</p>
                <p>Click "Report Side Effect" to get started.</p>
              </div>
            ) : (
              sideEffects.map((sideEffect) => (
                <div key={sideEffect.id} className="tracking-card side-effect">
                  <div className="card-header">
                    <h3>{sideEffect.medication?.drug_name}</h3>
                    <span className={`severity-badge severity-${sideEffect.severity}`}>
                      {sideEffect.severity}
                    </span>
                  </div>
                  <div className="card-body">
                    <p className="description">{sideEffect.description}</p>
                    <p className="timestamp">
                      <strong>Occurred:</strong> {formatEasternDateTime(sideEffect.occurred_at)}
                    </p>
                  </div>
                  <div className="card-actions">
                    <button
                      className="btn-delete"
                      onClick={() => handleDeleteSideEffect(sideEffect.id)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {activeTab === 'symptoms' && (
        <div className="tab-content">
          <div className="section-header">
            <h2>Symptom Tracking</h2>
            <button
              className="btn btn-primary"
              onClick={() => setShowSymptomForm(!showSymptomForm)}
            >
              {showSymptomForm ? 'Cancel' : '+ Track Symptom'}
            </button>
          </div>

          {showSymptomForm && (
            <SymptomTracker
              onSuccess={handleSymptomSuccess}
              onCancel={() => setShowSymptomForm(false)}
            />
          )}

          <div className="tracking-list">
            {symptoms.length === 0 ? (
              <div className="empty-state">
                <p>No symptoms tracked yet.</p>
                <p>Click "Track Symptom" to get started.</p>
              </div>
            ) : (
              symptoms.map((symptom) => (
                <div key={symptom.id} className="tracking-card symptom">
                  <div className="card-header">
                    <h3>{symptom.symptom_name}</h3>
                    <div className="improvement-indicator">
                      <span className="improvement-level">{symptom.improvement_level}/10</span>
                    </div>
                  </div>
                  <div className="card-body">
                    <p>
                      <strong>Medication:</strong> {symptom.medication?.drug_name}
                    </p>
                    {symptom.notes && (
                      <p className="notes">
                        <strong>Notes:</strong> {symptom.notes}
                      </p>
                    )}
                    <p className="timestamp">
                      <strong>Recorded:</strong> {formatEasternDateTime(symptom.recorded_at)}
                    </p>
                  </div>
                  <div className="card-actions">
                    <button
                      className="btn-delete"
                      onClick={() => handleDeleteSymptom(symptom.id)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default TrackingPage
