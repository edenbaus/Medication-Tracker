import { useState, useEffect } from 'react'
import medicationService from '../../services/medicationService'
import sideEffectService from '../../services/sideEffectService'
import { formatDateTimeForInput, formatEasternDateTime } from '../../utils/dateUtils'
import './TrackingForms.css'

function SideEffectForm({ onSuccess, onCancel, initialData = null }) {
  const [medications, setMedications] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [formData, setFormData] = useState({
    medication_id: initialData?.medication_id || '',
    severity: initialData?.severity || 'mild',
    description: initialData?.description || '',
    occurred_at: initialData?.occurred_at
      ? formatDateTimeForInput(initialData.occurred_at)
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
      // Convert datetime-local to ISO string
      const submitData = {
        ...formData,
        occurred_at: new Date(formData.occurred_at).toISOString(),
      }

      if (initialData) {
        await sideEffectService.updateSideEffect(initialData.id, submitData)
      } else {
        await sideEffectService.createSideEffect(submitData)
      }

      if (onSuccess) {
        onSuccess()
      }
    } catch (err) {
      console.error('Failed to save side effect:', err)
      setError(err.response?.data?.detail || 'Failed to save side effect')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="tracking-form">
      <h3>{initialData ? 'Edit' : 'Report'} Side Effect</h3>

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
          <label htmlFor="severity">Severity *</label>
          <select
            id="severity"
            name="severity"
            value={formData.severity}
            onChange={handleInputChange}
            required
          >
            <option value="mild">Mild</option>
            <option value="moderate">Moderate</option>
            <option value="severe">Severe</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="occurred_at">When did it occur? *</label>
          <input
            type="datetime-local"
            id="occurred_at"
            name="occurred_at"
            value={formData.occurred_at}
            onChange={handleInputChange}
            required
          />
          <small className="help-text">Times are in US Eastern timezone</small>
        </div>

        <div className="form-group">
          <label htmlFor="description">Description *</label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleInputChange}
            rows="4"
            required
            placeholder="Describe the side effect you experienced..."
          />
        </div>

        {error && <div className="error">{error}</div>}

        <div className="form-actions">
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Saving...' : initialData ? 'Update' : 'Report'} Side Effect
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

export default SideEffectForm
