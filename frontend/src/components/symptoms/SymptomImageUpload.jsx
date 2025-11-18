import { useState, useRef } from 'react'
import symptomService from '../../services/symptomService'
import './SymptomImages.css'

function SymptomImageUpload({ symptomId, onUploadComplete }) {
  const [selectedFiles, setSelectedFiles] = useState([])
  const [previews, setPreviews] = useState([])
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const fileInputRef = useRef(null)

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files)

    // Validate file count
    if (files.length + selectedFiles.length > 10) {
      setError('Maximum 10 images can be uploaded at once')
      return
    }

    // Validate file types and sizes
    const validFiles = []
    const newPreviews = []

    for (const file of files) {
      // Check file type
      if (!file.type.startsWith('image/')) {
        setError(`${file.name} is not an image file`)
        continue
      }

      // Check file size (10MB max)
      if (file.size > 10 * 1024 * 1024) {
        setError(`${file.name} is too large (max 10MB)`)
        continue
      }

      validFiles.push(file)

      // Create preview
      const reader = new FileReader()
      reader.onloadend = () => {
        newPreviews.push({
          file,
          url: reader.result,
        })

        if (newPreviews.length === validFiles.length) {
          setPreviews([...previews, ...newPreviews])
        }
      }
      reader.readAsDataURL(file)
    }

    setSelectedFiles([...selectedFiles, ...validFiles])
    setError('')
  }

  const removeFile = (index) => {
    const newFiles = [...selectedFiles]
    const newPreviews = [...previews]
    newFiles.splice(index, 1)
    newPreviews.splice(index, 1)
    setSelectedFiles(newFiles)
    setPreviews(newPreviews)
  }

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      setError('Please select at least one image')
      return
    }

    setUploading(true)
    setError('')

    try {
      await symptomService.uploadSymptomImages(symptomId, selectedFiles)

      // Reset state
      setSelectedFiles([])
      setPreviews([])
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }

      // Notify parent component
      if (onUploadComplete) {
        onUploadComplete()
      }
    } catch (err) {
      console.error('Error uploading images:', err)
      setError(err.response?.data?.detail || 'Failed to upload images')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="symptom-image-upload">
      <h3>Upload Images</h3>

      <div className="upload-section">
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept="image/*"
          onChange={handleFileSelect}
          className="file-input"
          id="symptom-image-input"
        />
        <label htmlFor="symptom-image-input" className="file-input-label">
          <svg className="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
          Choose Images
        </label>
        <p className="file-input-hint">
          Select up to 10 images (JPG, PNG, GIF, WebP, HEIC, HEIF) - Max 10MB each
        </p>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {previews.length > 0 && (
        <div className="preview-section">
          <h4>Selected Images ({previews.length})</h4>
          <div className="preview-grid">
            {previews.map((preview, index) => (
              <div key={index} className="preview-item">
                <img src={preview.url} alt={`Preview ${index + 1}`} />
                <button
                  type="button"
                  className="remove-btn"
                  onClick={() => removeFile(index)}
                  aria-label="Remove image"
                >
                  ×
                </button>
                <p className="file-name">{preview.file.name}</p>
              </div>
            ))}
          </div>

          <button
            type="button"
            className="upload-btn"
            onClick={handleUpload}
            disabled={uploading}
          >
            {uploading ? 'Uploading...' : `Upload ${selectedFiles.length} Image${selectedFiles.length !== 1 ? 's' : ''}`}
          </button>
        </div>
      )}
    </div>
  )
}

export default SymptomImageUpload
