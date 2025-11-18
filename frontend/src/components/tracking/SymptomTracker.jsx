import { useState, useEffect } from 'react'
import medicationService from '../../services/medicationService'
import symptomService from '../../services/symptomService'
import { formatDateTimeForInput, formatEasternDateTime } from '../../utils/dateUtils'
import './TrackingForms.css'

function SymptomTracker({ onSuccess, onCancel, initialData = null }) {
  const [medications, setMedications] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [formData, setFormData] = useState({
    medication_id: initialData?.medication_id || '',
    symptom_name: initialData?.symptom_name || '',
    improvement_level: initialData?.improvement_level || 5,
    notes: initialData?.notes || '',
    recorded_at: initialData?.recorded_at
      ? formatDateTimeForInput(initialData.recorded_at)
      : formatDateTimeForInput(new Date()),
  })

  useEffect(() => {
    fetchMedications()
  }, [])

  const fetchMedications = async () => {
    try {
      const data = await medicationService.getMedications({ active: true })
      setMedications(data.medications || [])
    } catch (err) {
      console.error('Failed to fetch medications:', err)
      setError('Failed to load medications')
    }
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData({
      ...formData,
      [name]: value,
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      // Validate improvement level
      const improvementLevel = parseInt(formData.improvement_level)
      if (improvementLevel < 1 || improvementLevel > 10) {
        setError('Improvement level must be between 1 and 10')
        setLoading(false)
        return
      }

      // Convert datetime-local to ISO string
      const submitData = {
        ...formData,
        improvement_level: improvementLevel,
        recorded_at: new Date(formData.recorded_at).toISOString(),
      }

      if (initialData) {
        await symptomService.updateSymptom(initialData.id, submitData)
      } else {
        await symptomService.createSymptom(submitData)
      }

      if (onSuccess) {
        onSuccess()
      }
    } catch (err) {
      console.error('Failed to save symptom tracking:', err)
      setError(err.response?.data?.detail || 'Failed to save symptom tracking')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="tracking-form">
      <h3>{initialData ? 'Edit' : 'Track'} Symptom</h3>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="medication_id">Medication *</label>
          <select
            id="medication_id"
            name="medication_id"
            value={formData.medication_id}
            onChange={handleInputChange}
            required
            disabled={initialData !== null}
          >
            <option value="">Select medication</option>
            {medications.map((med) => (
              <option key={med.id} value={med.id}>
                {med.drug_name} ({med.standard_dose})
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="symptom_name">Symptom *</label>
          <input
            type="text"
            id="symptom_name"
            name="symptom_name"
            value={formData.symptom_name}
            onChange={handleInputChange}
            required
            placeholder="e.g., Headache, Nausea, Pain"
          />
        </div>

        <div className="form-group">
          <label htmlFor="improvement_level">
            Improvement Level * (1-10)
            <span className="improvement-value">{formData.improvement_level}</span>
          </label>
          <input
            type="range"
            id="improvement_level"
            name="improvement_level"
            min="1"
            max="10"
            value={formData.improvement_level}
            onChange={handleInputChange}
            required
            className="improvement-slider"
          />
          <div className="improvement-scale">
            <span>1 (Worse)</span>
            <span>5 (No Change)</span>
            <span>10 (Much Better)</span>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="recorded_at">When recorded? *</label>
          <input
            type="datetime-local"
            id="recorded_at"
            name="recorded_at"
            value={formData.recorded_at}
            onChange={handleInputChange}
            required
          />
          <small className="help-text">Times are in US Eastern timezone</small>
        </div>

        <div className="form-group">
          <label htmlFor="notes">Notes (optional)</label>
          <textarea
            id="notes"
            name="notes"
            value={formData.notes}
            onChange={handleInputChange}
            rows="3"
            placeholder="Additional notes about the symptom or improvement..."
          />
        </div>

        {error && <div className="error">{error}</div>}

        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Saving...' : initialData ? 'Update' : 'Track'} Symptom
          </button>
          {onCancel && (
            <button type="button" className="btn btn-secondary" onClick={onCancel}>
              Cancel
            </button>
          )}
        </div>
      </form>
    </div>
  )
}

export default SymptomTracker
