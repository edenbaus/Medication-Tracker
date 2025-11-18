# Symptom Image Upload Feature

This feature allows users to upload one or more images for each symptom tracking entry. This is useful for documenting visual symptoms like rashes, swelling, bruising, etc.

## Features

- **Multiple Image Upload**: Upload up to 10 images per symptom
- **Image Preview**: Preview images before uploading
- **Image Gallery**: View all uploaded images in a responsive grid
- **Full-Screen Viewer**: Click on any image to view it in full-screen modal
- **Image Management**: Delete images individually
- **File Validation**: Automatic validation of file types and sizes
- **Supported Formats**: JPG, JPEG, PNG, GIF, WebP, HEIC, HEIF
- **Size Limit**: 10MB per image

## Backend Implementation

### Database Schema

A new `symptom_images` table has been created with the following structure:

```sql
CREATE TABLE symptom_images (
    id UUID PRIMARY KEY,
    symptom_id UUID REFERENCES symptom_tracking(id) ON DELETE CASCADE,
    filename VARCHAR NOT NULL,
    file_path VARCHAR NOT NULL,
    file_size VARCHAR,
    content_type VARCHAR,
    uploaded_at TIMESTAMP NOT NULL
);
```

### API Endpoints

#### 1. Get Symptom with Images
```
GET /api/symptoms/{symptom_id}/with-images
```
Returns a symptom tracking entry with all associated images.

**Response:**
```json
{
  "id": "uuid",
  "symptom_name": "Headache",
  "improvement_level": 7,
  "notes": "Much better today",
  "recorded_at": "2025-11-18T10:00:00",
  "images": [
    {
      "id": "uuid",
      "symptom_id": "uuid",
      "filename": "photo.jpg",
      "file_path": "/app/uploads/symptom-id/unique-filename.jpg",
      "file_size": "2048000",
      "content_type": "image/jpeg",
      "uploaded_at": "2025-11-18T10:05:00"
    }
  ]
}
```

#### 2. Upload Images
```
POST /api/symptoms/{symptom_id}/images
Content-Type: multipart/form-data
```
Upload one or more images for a symptom.

**Request:**
- Form data with `files` field containing image files
- Maximum 10 files per request
- Maximum 10MB per file

**Response:**
```json
[
  {
    "id": "uuid",
    "symptom_id": "uuid",
    "filename": "photo.jpg",
    "file_path": "/app/uploads/symptom-id/unique-filename.jpg",
    "file_size": "2048000",
    "content_type": "image/jpeg",
    "uploaded_at": "2025-11-18T10:05:00"
  }
]
```

#### 3. Delete Image
```
DELETE /api/symptoms/{symptom_id}/images/{image_id}
```
Delete a specific image from a symptom.

**Response:** 204 No Content

#### 4. Serve Static Files
```
GET /uploads/{symptom_id}/{filename}
```
Serves uploaded images as static files.

### File Storage

Images are stored in the Docker volume `symptom_uploads` which is mounted to `/app/uploads` in the container. Each symptom has its own subdirectory:

```
/app/uploads/
  ├── {symptom-id-1}/
  │   ├── unique-filename-1.jpg
  │   └── unique-filename-2.png
  └── {symptom-id-2}/
      └── unique-filename-3.jpg
```

## Frontend Components

### 1. SymptomImageUpload

Component for uploading images to a symptom.

**Props:**
- `symptomId` (string, required): The symptom ID
- `onUploadComplete` (function, optional): Callback called after successful upload

**Usage:**
```jsx
import SymptomImageUpload from './components/symptoms/SymptomImageUpload'

function MyComponent() {
  const handleUploadComplete = () => {
    console.log('Upload complete!')
    // Reload symptom data
  }

  return (
    <SymptomImageUpload
      symptomId="symptom-uuid"
      onUploadComplete={handleUploadComplete}
    />
  )
}
```

### 2. SymptomImageGallery

Component for displaying and managing symptom images.

**Props:**
- `images` (array, required): Array of image objects
- `symptomId` (string, required): The symptom ID
- `onImageDeleted` (function, optional): Callback called after image deletion

**Usage:**
```jsx
import SymptomImageGallery from './components/symptoms/SymptomImageGallery'

function MyComponent() {
  const [images, setImages] = useState([])

  const handleImageDeleted = (imageId) => {
    setImages(images.filter(img => img.id !== imageId))
  }

  return (
    <SymptomImageGallery
      images={images}
      symptomId="symptom-uuid"
      onImageDeleted={handleImageDeleted}
    />
  )
}
```

### 3. SymptomDetail (Example)

A complete example showing how to use both components together.

**Usage:**
```jsx
import SymptomDetail from './components/symptoms/SymptomDetail'

// In your router:
<Route path="/symptoms/:symptomId" element={<SymptomDetail />} />
```

## Service Methods

### symptomService

**New methods added:**

```javascript
// Get symptom with images
const symptom = await symptomService.getSymptomWithImages(symptomId)

// Upload images
const uploadedImages = await symptomService.uploadSymptomImages(
  symptomId,
  [file1, file2, file3]
)

// Delete image
await symptomService.deleteSymptomImage(symptomId, imageId)

// Get image URL for display
const imageUrl = symptomService.getImageUrl(imagePath)
```

## Docker Configuration

The `docker-compose.yml` has been updated to include a volume for persistent image storage:

```yaml
volumes:
  - symptom_uploads:/app/uploads

volumes:
  symptom_uploads:
```

This ensures uploaded images persist even when containers are restarted.

## Security Considerations

1. **File Type Validation**: Only image files are accepted (checked by MIME type and extension)
2. **File Size Limits**: Maximum 10MB per file to prevent abuse
3. **Upload Limits**: Maximum 10 files per upload request
4. **Authentication**: All endpoints require authentication
5. **Authorization**: Users can only access their own symptom images
6. **Unique Filenames**: Files are stored with UUID-based filenames to prevent conflicts

## Testing

To test the image upload feature:

1. Start the application:
   ```bash
   docker-compose up
   ```

2. Create a symptom tracking entry

3. Navigate to the symptom detail page

4. Use the upload interface to select and upload images

5. View images in the gallery

6. Click on images to view them in full-screen

7. Delete images using the delete buttons

## File Structure

```
backend/
├── app/
│   ├── models/
│   │   ├── symptom.py (updated)
│   │   └── symptom_image.py (new)
│   ├── schemas/
│   │   └── symptom.py (updated)
│   ├── api/
│   │   └── v1/
│   │       └── symptoms.py (updated)
│   ├── utils/
│   │   └── file_upload.py (new)
│   └── main.py (updated)
└── alembic/
    └── versions/
        └── {timestamp}_add_symptom_images_table.py (new)

frontend/
└── src/
    ├── components/
    │   └── symptoms/
    │       ├── SymptomImageUpload.jsx (new)
    │       ├── SymptomImageGallery.jsx (new)
    │       ├── SymptomDetail.jsx (new)
    │       └── SymptomImages.css (new)
    └── services/
        └── symptomService.js (updated)
```

## Future Enhancements

Potential improvements for the future:

1. **Image Compression**: Automatically compress images on upload
2. **Thumbnails**: Generate thumbnails for faster loading
3. **Batch Delete**: Delete multiple images at once
4. **Image Editing**: Basic editing capabilities (crop, rotate, etc.)
5. **Cloud Storage**: Option to store images in S3 or similar
6. **Image Captions**: Add captions or notes to individual images
7. **Download All**: Download all images as a ZIP file
8. **Comparison View**: Side-by-side comparison of images over time

## Troubleshooting

### Images not displaying

1. Check that the backend is serving static files correctly:
   ```
   curl http://localhost:8000/uploads/test.jpg
   ```

2. Verify the `VITE_API_URL` environment variable is set correctly

3. Check browser console for CORS errors

### Upload fails

1. Check file size is under 10MB
2. Verify file is a valid image format
3. Check backend logs for detailed error messages
4. Ensure uploads directory has correct permissions

### Images disappear after restart

1. Verify the Docker volume is properly configured
2. Check that volume is not being deleted on `docker-compose down`
3. Use `docker volume ls` to list volumes

---

**Last Updated**: 2025-11-18
