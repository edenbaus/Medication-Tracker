import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import symptomService from '../../services/symptomService'
import SymptomImageUpload from './SymptomImageUpload'
import SymptomImageGallery from './SymptomImageGallery'
import './SymptomImages.css'

/**
 * Example component showing how to use SymptomImageUpload and SymptomImageGallery together
 *
 * Usage:
 * import SymptomDetail from './components/symptoms/SymptomDetail'
 *
 * <Route path="/symptoms/:symptomId" element={<SymptomDetail />} />
 */
function SymptomDetail() {
  const { symptomId } = useParams()
  const [symptom, setSymptom] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadSymptom = async () => {
    setLoading(true)
    setError('')

    try {
      const data = await symptomService.getSymptomWithImages(symptomId)
      setSymptom(data)
    } catch (err) {
      console.error('Error loading symptom:', err)
      setError(err.response?.data?.detail || 'Failed to load symptom details')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (symptomId) {
      loadSymptom()
    }
  }, [symptomId])

  const handleUploadComplete = () => {
    // Reload symptom data to show newly uploaded images
    loadSymptom()
  }

  const handleImageDeleted = (imageId) => {
    // Remove deleted image from state
    setSymptom((prev) => ({
      ...prev,
      images: prev.images.filter((img) => img.id !== imageId),
    }))
  }

  if (loading) {
    return (
      <div className="symptom-detail">
        <p>Loading symptom details...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="symptom-detail">
        <div className="error-message">{error}</div>
      </div>
    )
  }

  if (!symptom) {
    return (
      <div className="symptom-detail">
        <p>Symptom not found</p>
      </div>
    )
  }

  return (
    <div className="symptom-detail">
      <div className="symptom-header">
        <h1>{symptom.symptom_name}</h1>
        <div className="symptom-info">
          <p><strong>Improvement Level:</strong> {symptom.improvement_level}/10</p>
          <p><strong>Recorded:</strong> {new Date(symptom.recorded_at).toLocaleString()}</p>
          {symptom.notes && (
            <p><strong>Notes:</strong> {symptom.notes}</p>
          )}
        </div>
      </div>

      <SymptomImageUpload
        symptomId={symptomId}
        onUploadComplete={handleUploadComplete}
      />

      <SymptomImageGallery
        images={symptom.images || []}
        symptomId={symptomId}
        onImageDeleted={handleImageDeleted}
      />
    </div>
  )
}

export default SymptomDetail
