import { useState } from 'react'
import symptomService from '../../services/symptomService'
import './SymptomImages.css'

function SymptomImageGallery({ images, symptomId, onImageDeleted }) {
  const [selectedImage, setSelectedImage] = useState(null)
  const [deleting, setDeleting] = useState(null)
  const [error, setError] = useState('')

  const handleImageClick = (image) => {
    setSelectedImage(image)
  }

  const handleCloseModal = () => {
    setSelectedImage(null)
  }

  const handleDeleteImage = async (imageId) => {
    if (!window.confirm('Are you sure you want to delete this image?')) {
      return
    }

    setDeleting(imageId)
    setError('')

    try {
      await symptomService.deleteSymptomImage(symptomId, imageId)

      // Close modal if deleting the currently viewed image
      if (selectedImage && selectedImage.id === imageId) {
        setSelectedImage(null)
      }

      // Notify parent component
      if (onImageDeleted) {
        onImageDeleted(imageId)
      }
    } catch (err) {
      console.error('Error deleting image:', err)
      setError(err.response?.data?.detail || 'Failed to delete image')
    } finally {
      setDeleting(null)
    }
  }

  const formatFileSize = (bytes) => {
    if (!bytes) return 'Unknown size'
    const kb = parseInt(bytes) / 1024
    if (kb < 1024) {
      return `${kb.toFixed(1)} KB`
    }
    return `${(kb / 1024).toFixed(1)} MB`
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleString()
  }

  if (!images || images.length === 0) {
    return (
      <div className="symptom-image-gallery empty">
        <p className="empty-message">No images uploaded yet</p>
      </div>
    )
  }

  return (
    <div className="symptom-image-gallery">
      <h3>Images ({images.length})</h3>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="gallery-grid">
        {images.map((image) => (
          <div key={image.id} className="gallery-item">
            <div className="image-container" onClick={() => handleImageClick(image)}>
              <img
                src={symptomService.getImageUrl(image.file_path)}
                alt={image.filename}
                className="gallery-image"
              />
              <div className="image-overlay">
                <span className="view-text">View</span>
              </div>
            </div>
            <div className="image-info">
              <p className="image-filename" title={image.filename}>
                {image.filename}
              </p>
              <p className="image-meta">
                {formatFileSize(image.file_size)}
              </p>
              <button
                className="delete-btn"
                onClick={() => handleDeleteImage(image.id)}
                disabled={deleting === image.id}
              >
                {deleting === image.id ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Image Modal */}
      {selectedImage && (
        <div className="image-modal" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={handleCloseModal}>
              ×
            </button>
            <img
              src={symptomService.getImageUrl(selectedImage.file_path)}
              alt={selectedImage.filename}
              className="modal-image"
            />
            <div className="modal-info">
              <h4>{selectedImage.filename}</h4>
              <div className="modal-details">
                <p><strong>Size:</strong> {formatFileSize(selectedImage.file_size)}</p>
                <p><strong>Type:</strong> {selectedImage.content_type}</p>
                <p><strong>Uploaded:</strong> {formatDate(selectedImage.uploaded_at)}</p>
              </div>
              <button
                className="modal-delete-btn"
                onClick={() => handleDeleteImage(selectedImage.id)}
                disabled={deleting === selectedImage.id}
              >
                {deleting === selectedImage.id ? 'Deleting...' : 'Delete Image'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default SymptomImageGallery
