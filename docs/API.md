# Medication Tracker API Documentation

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Medications](#medications)
- [Tags](#tags)
- [Admin](#admin)
- [Error Responses](#error-responses)
- [Data Models](#data-models)

## Overview

The Medication Tracker API is a RESTful API built with FastAPI. It provides endpoints for managing medications, tracking medication intake, and organizing medications using custom tags.

**Base URL**: `http://localhost:8000/api`

**API Documentation**: `http://localhost:8000/docs` (Swagger UI)

### API Versioning

All API endpoints are versioned. Current version: `v1`

### Content Type

All requests and responses use JSON format:
- Request header: `Content-Type: application/json`
- Response header: `Content-Type: application/json`

## Authentication

### Register New User

Create a new user account.

**Endpoint**: `POST /auth/register`

**Request Body**:
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securePassword123"
}
```

**Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "johndoe",
  "email": "john@example.com",
  "created_at": "2025-11-16T10:30:00Z",
  "updated_at": "2025-11-16T10:30:00Z"
}
```

### Login

Authenticate and receive an access token.

**Endpoint**: `POST /auth/login`

**Request Body** (form data):
```
username=john@example.com
password=securePassword123
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Get Current User

Get information about the currently authenticated user.

**Endpoint**: `GET /auth/me`

**Headers**:
```
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "johndoe",
  "email": "john@example.com",
  "created_at": "2025-11-16T10:30:00Z",
  "updated_at": "2025-11-16T10:30:00Z"
}
```

### OAuth Login (Google)

Login using Google OAuth.

**Step 1 - Initiate Login**:

**Endpoint**: `GET /auth/google/login`

Redirects user to Google's authorization page. User grants permissions and is redirected back to the callback URL.

**Step 2 - Callback**:

**Endpoint**: `GET /auth/google/callback`

**Query Parameters** (automatically provided by Google):
- `code`: Authorization code
- `state`: State parameter

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses**:
- `400 Bad Request`: Failed to get user info or missing email
- `501 Not Implemented`: Google OAuth not configured (missing credentials)
- `500 Internal Server Error`: OAuth authentication failed

**Notes**:
- If user already exists with the same email, their account is linked to Google OAuth
- New users are automatically created with username based on email
- OAuth users cannot login with password (must use OAuth)

### OAuth Login (GitHub)

Login using GitHub OAuth.

**Step 1 - Initiate Login**:

**Endpoint**: `GET /auth/github/login`

Redirects user to GitHub's authorization page. User grants permissions and is redirected back to the callback URL.

**Step 2 - Callback**:

**Endpoint**: `GET /auth/github/callback`

**Query Parameters** (automatically provided by GitHub):
- `code`: Authorization code
- `state`: State parameter

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Error Responses**:
- `400 Bad Request`: No verified email found in GitHub account
- `501 Not Implemented`: GitHub OAuth not configured (missing credentials)
- `500 Internal Server Error`: OAuth authentication failed

**Notes**:
- Requires verified email in GitHub account
- If user already exists with the same email, their account is linked to GitHub OAuth
- New users are automatically created with username based on GitHub login
- OAuth users cannot login with password (must use OAuth)

## Medications

All medication endpoints require authentication via Bearer token.

### List Medications

Get a paginated list of medications with optional filtering.

**Endpoint**: `GET /medications/`

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | integer | 0 | Number of records to skip (pagination) |
| `limit` | integer | 50 | Maximum records to return (max: 100) |
| `active` | boolean | - | Filter by active status |
| `prescription_type` | string | - | Filter by type: `long_term`, `short_term`, `otc` |
| `tag_ids` | array[UUID] | - | Filter by tag IDs (returns medications with ANY of the tags) |

**Example Request**:
```
GET /medications/?active=true&prescription_type=long_term&skip=0&limit=20
```

**Response** (200 OK):
```json
{
  "medications": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "drug_name": "Lisinopril",
      "pharmacy": "CVS Pharmacy",
      "prescription_type": "long_term",
      "dosing_schedule": {
        "frequency": "daily",
        "times": ["08:00"],
        "with_food": false
      },
      "standard_dose": "10mg",
      "date_prescribed": "2025-01-15",
      "date_filled": "2025-01-15",
      "prescribing_doctor": "Dr. Smith",
      "prescription_number": "RX123456",
      "notes": "For blood pressure management",
      "active": true,
      "start_date": "2025-01-15",
      "end_date": null,
      "tags": [
        {
          "id": "789e4567-e89b-12d3-a456-426614174000",
          "name": "Morning",
          "color": "#FF5733"
        },
        {
          "id": "456e4567-e89b-12d3-a456-426614174000",
          "name": "Heart Health",
          "color": "#33C3FF"
        }
      ],
      "created_at": "2025-01-15T10:00:00Z",
      "updated_at": "2025-01-15T10:00:00Z"
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 20
}
```

### Create Medication

Create a new medication entry.

**Endpoint**: `POST /medications/`

**Request Body**:
```json
{
  "drug_name": "Aspirin",
  "pharmacy": "Walgreens",
  "prescription_type": "otc",
  "dosing_schedule": {
    "frequency": "as needed",
    "max_daily": 4
  },
  "standard_dose": "325mg",
  "date_prescribed": null,
  "date_filled": "2025-11-16",
  "prescribing_doctor": null,
  "prescription_number": null,
  "notes": "For occasional headaches",
  "active": true,
  "start_date": "2025-11-16",
  "end_date": null,
  "tag_ids": ["789e4567-e89b-12d3-a456-426614174000"]
}
```

**Required Fields**:
- `drug_name`
- `standard_dose`
- `start_date`

**Response** (201 Created):
```json
{
  "id": "abc12345-e89b-12d3-a456-426614174000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "drug_name": "Aspirin",
  "pharmacy": "Walgreens",
  "prescription_type": "otc",
  "dosing_schedule": {
    "frequency": "as needed",
    "max_daily": 4
  },
  "standard_dose": "325mg",
  "date_prescribed": null,
  "date_filled": "2025-11-16",
  "prescribing_doctor": null,
  "prescription_number": null,
  "notes": "For occasional headaches",
  "active": true,
  "start_date": "2025-11-16",
  "end_date": null,
  "tags": [
    {
      "id": "789e4567-e89b-12d3-a456-426614174000",
      "name": "As Needed",
      "color": "#FFA500"
    }
  ],
  "created_at": "2025-11-16T14:30:00Z",
  "updated_at": "2025-11-16T14:30:00Z"
}
```

### Get Medication by ID

Retrieve a specific medication by its ID.

**Endpoint**: `GET /medications/{medication_id}`

**Response** (200 OK):
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "drug_name": "Lisinopril",
  ...
}
```

**Error Response** (404 Not Found):
```json
{
  "detail": "Medication not found"
}
```

### Update Medication

Update an existing medication. All fields are optional.

**Endpoint**: `PUT /medications/{medication_id}`

**Request Body** (partial update):
```json
{
  "standard_dose": "20mg",
  "notes": "Increased dosage per doctor's recommendation"
}
```

**Response** (200 OK):
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "drug_name": "Lisinopril",
  "standard_dose": "20mg",
  "notes": "Increased dosage per doctor's recommendation",
  ...
}
```

### Delete Medication

Soft delete a medication by setting `active=false`.

**Endpoint**: `DELETE /medications/{medication_id}`

**Response** (204 No Content)

### Add Tag to Medication

Associate a tag with a medication.

**Endpoint**: `POST /medications/{medication_id}/tags/{tag_id}`

**Response** (200 OK):
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "drug_name": "Lisinopril",
  "tags": [
    {
      "id": "789e4567-e89b-12d3-a456-426614174000",
      "name": "Morning",
      "color": "#FF5733"
    }
  ],
  ...
}
```

**Error Response** (400 Bad Request):
```json
{
  "detail": "Tag is already assigned to this medication"
}
```

### Remove Tag from Medication

Remove a tag association from a medication.

**Endpoint**: `DELETE /medications/{medication_id}/tags/{tag_id}`

**Response** (200 OK):
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "drug_name": "Lisinopril",
  "tags": [],
  ...
}
```

## Tags

All tag endpoints require authentication via Bearer token.

### List Tags

Get all tags for the current user.

**Endpoint**: `GET /tags/`

**Response** (200 OK):
```json
{
  "tags": [
    {
      "id": "789e4567-e89b-12d3-a456-426614174000",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Morning",
      "color": "#FF5733",
      "created_at": "2025-01-10T09:00:00Z",
      "updated_at": "2025-01-10T09:00:00Z"
    },
    {
      "id": "456e4567-e89b-12d3-a456-426614174000",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Heart Health",
      "color": "#33C3FF",
      "created_at": "2025-01-10T09:05:00Z",
      "updated_at": "2025-01-10T09:05:00Z"
    }
  ],
  "total": 2
}
```

### List Tags with Medication Counts

Get tags with the count of active medications for each tag.

**Endpoint**: `GET /tags/with-counts`

**Response** (200 OK):
```json
[
  {
    "id": "789e4567-e89b-12d3-a456-426614174000",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Morning",
    "color": "#FF5733",
    "medication_count": 5,
    "created_at": "2025-01-10T09:00:00Z",
    "updated_at": "2025-01-10T09:00:00Z"
  },
  {
    "id": "456e4567-e89b-12d3-a456-426614174000",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "As Needed",
    "color": "#FFA500",
    "medication_count": 0,
    "created_at": "2025-01-10T09:05:00Z",
    "updated_at": "2025-01-10T09:05:00Z"
  }
]
```

### Create Tag

Create a new tag for organizing medications.

**Endpoint**: `POST /tags/`

**Request Body**:
```json
{
  "name": "Evening",
  "color": "#9B59B6"
}
```

**Required Fields**:
- `name` (1-100 characters, unique per user)

**Optional Fields**:
- `color` (hex color code, format: #RRGGBB)

**Response** (201 Created):
```json
{
  "id": "def12345-e89b-12d3-a456-426614174000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Evening",
  "color": "#9B59B6",
  "created_at": "2025-11-16T14:45:00Z",
  "updated_at": "2025-11-16T14:45:00Z"
}
```

**Error Response** (400 Bad Request):
```json
{
  "detail": "Tag with name 'Evening' already exists"
}
```

### Get Tag by ID

Retrieve a specific tag by its ID.

**Endpoint**: `GET /tags/{tag_id}`

**Response** (200 OK):
```json
{
  "id": "789e4567-e89b-12d3-a456-426614174000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Morning",
  "color": "#FF5733",
  "created_at": "2025-01-10T09:00:00Z",
  "updated_at": "2025-01-10T09:00:00Z"
}
```

### Update Tag

Update a tag's name or color.

**Endpoint**: `PUT /tags/{tag_id}`

**Request Body** (partial update):
```json
{
  "color": "#E74C3C"
}
```

**Response** (200 OK):
```json
{
  "id": "789e4567-e89b-12d3-a456-426614174000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Morning",
  "color": "#E74C3C",
  "created_at": "2025-01-10T09:00:00Z",
  "updated_at": "2025-11-16T15:00:00Z"
}
```

### Delete Tag

Delete a tag. This will remove the tag from all medications (CASCADE).

**Endpoint**: `DELETE /tags/{tag_id}`

**Response** (204 No Content)

### Get Medications for Tag

Get all active medication IDs associated with a specific tag.

**Endpoint**: `GET /tags/{tag_id}/medications`

**Response** (200 OK):
```json
[
  "123e4567-e89b-12d3-a456-426614174000",
  "abc12345-e89b-12d3-a456-426614174000",
  "def12345-e89b-12d3-a456-426614174000"
]
```

## Medication Logs

Track when medications are taken with medication logs. All log endpoints require authentication.

### Create Medication Log

Log that a medication was taken.

**Endpoint**: `POST /logs/`

**Headers**:
```
Authorization: Bearer <access_token>
```

**Request Body**:
```json
{
  "medication_id": "123e4567-e89b-12d3-a456-426614174000",
  "dose_taken": "10mg",
  "taken_at": "2025-11-16T14:30:00Z",
  "notes": "Took with food"
}
```

**Fields**:
- `medication_id` (required): UUID of the medication
- `dose_taken` (required): Dose amount (e.g., "10mg", "2 tablets")
- `taken_at` (optional): When medication was taken (defaults to current time)
- `notes` (optional): Additional notes

**Response** (201 Created):
```json
{
  "id": "log-uuid-here",
  "medication_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "user-uuid-here",
  "dose_taken": "10mg",
  "taken_at": "2025-11-16T14:30:00Z",
  "notes": "Took with food",
  "created_at": "2025-11-16T14:30:00Z"
}
```

**Error Responses**:
- `404 Not Found`: Medication not found
- `422 Unprocessable Entity`: Validation error (future time, empty dose, etc.)

### List Medication Logs

Get all medication logs for the current user with optional filtering.

**Endpoint**: `GET /logs/`

**Query Parameters**:
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum records to return (default: 50, max: 100)
- `medication_id` (optional): Filter by specific medication UUID
- `start_date` (optional): Filter logs after this datetime (ISO 8601)
- `end_date` (optional): Filter logs before this datetime (ISO 8601)

**Response** (200 OK):
```json
{
  "logs": [
    {
      "id": "log-uuid-1",
      "medication_id": "med-uuid-1",
      "user_id": "user-uuid",
      "dose_taken": "10mg",
      "taken_at": "2025-11-16T14:30:00Z",
      "notes": "Took with food",
      "created_at": "2025-11-16T14:30:00Z"
    },
    {
      "id": "log-uuid-2",
      "medication_id": "med-uuid-1",
      "user_id": "user-uuid",
      "dose_taken": "10mg",
      "taken_at": "2025-11-15T14:30:00Z",
      "notes": null,
      "created_at": "2025-11-15T14:30:00Z"
    }
  ],
  "total": 45,
  "page": 1,
  "page_size": 50
}
```

### Get Single Log

Get details of a specific medication log entry.

**Endpoint**: `GET /logs/{log_id}`

**Response** (200 OK):
```json
{
  "id": "log-uuid-here",
  "medication_id": "med-uuid-here",
  "user_id": "user-uuid-here",
  "dose_taken": "10mg",
  "taken_at": "2025-11-16T14:30:00Z",
  "notes": "Took with food",
  "created_at": "2025-11-16T14:30:00Z"
}
```

**Error Responses**:
- `404 Not Found`: Log entry not found

### Update Medication Log

Update an existing medication log entry.

**Endpoint**: `PUT /logs/{log_id}`

**Request Body** (all fields optional):
```json
{
  "dose_taken": "20mg",
  "taken_at": "2025-11-16T15:00:00Z",
  "notes": "Updated note"
}
```

**Response** (200 OK):
```json
{
  "id": "log-uuid-here",
  "medication_id": "med-uuid-here",
  "user_id": "user-uuid-here",
  "dose_taken": "20mg",
  "taken_at": "2025-11-16T15:00:00Z",
  "notes": "Updated note",
  "created_at": "2025-11-16T14:30:00Z"
}
```

**Error Responses**:
- `404 Not Found`: Log entry not found
- `422 Unprocessable Entity`: Validation error

### Delete Medication Log

Delete a medication log entry.

**Endpoint**: `DELETE /logs/{log_id}`

**Response** (204 No Content)

**Error Responses**:
- `404 Not Found`: Log entry not found

### Get Adherence Statistics

Get medication adherence statistics showing logged doses vs expected doses.

**Endpoint**: `GET /logs/stats/adherence`

**Query Parameters**:
- `days` (optional): Number of days to analyze (default: 30, max: 365)
- `medication_id` (optional): Filter by specific medication

**Response** (200 OK):
```json
{
  "total_medications": 3,
  "total_logged_doses": 75,
  "average_adherence": 83.33,
  "period_start": "2025-10-17T00:00:00Z",
  "period_end": "2025-11-16T23:59:59Z",
  "medication_stats": [
    {
      "medication_id": "med-uuid-1",
      "medication_name": "Lisinopril",
      "total_expected_doses": 30,
      "total_logged_doses": 28,
      "adherence_percentage": 93.33,
      "period_start": "2025-10-17T00:00:00Z",
      "period_end": "2025-11-16T23:59:59Z"
    },
    {
      "medication_id": "med-uuid-2",
      "medication_name": "Metformin",
      "total_expected_doses": 30,
      "total_logged_doses": 22,
      "adherence_percentage": 73.33,
      "period_start": "2025-10-17T00:00:00Z",
      "period_end": "2025-11-16T23:59:59Z"
    }
  ]
}
```

**Notes**:
- Expected doses assume 1 dose per day (simplified calculation)
- In production, this would parse `dosing_schedule` for accurate expected doses
- Only includes active medications
- Adherence percentage = (logged doses / expected doses) × 100

## Admin

Admin endpoints are only accessible to users with admin privileges. All admin endpoints require authentication with an admin user account.

### Get All Users

Get a paginated list of all users (admin only).

**Endpoint**: `GET /admin/users`

**Query Parameters**:
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum records to return (default: 50, max: 100)
- `is_admin` (optional): Filter by admin status (true/false)

**Headers**:
```
Authorization: Bearer <admin_access_token>
```

**Response** (200 OK):
```json
{
  "users": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "johndoe",
      "email": "john@example.com",
      "is_admin": false,
      "created_at": "2025-11-16T10:30:00Z",
      "updated_at": "2025-11-16T10:30:00Z"
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "username": "admin",
      "email": "admin@example.com",
      "is_admin": true,
      "created_at": "2025-11-15T08:00:00Z",
      "updated_at": "2025-11-15T08:00:00Z"
    }
  ],
  "total": 2,
  "page": 1,
  "page_size": 50
}
```

**Error Responses**:
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Admin access required

### Get User by ID

Get details of a specific user (admin only).

**Endpoint**: `GET /admin/users/{user_id}`

**Headers**:
```
Authorization: Bearer <admin_access_token>
```

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "johndoe",
  "email": "john@example.com",
  "is_admin": false,
  "created_at": "2025-11-16T10:30:00Z",
  "updated_at": "2025-11-16T10:30:00Z"
}
```

**Error Responses**:
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Admin access required
- `404 Not Found`: User not found

### Update User

Update a user's details (admin only).

**Endpoint**: `PUT /admin/users/{user_id}`

**Headers**:
```
Authorization: Bearer <admin_access_token>
```

**Request Body** (all fields optional):
```json
{
  "username": "newusername",
  "email": "newemail@example.com",
  "is_admin": true
}
```

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "newusername",
  "email": "newemail@example.com",
  "is_admin": true,
  "created_at": "2025-11-16T10:30:00Z",
  "updated_at": "2025-11-16T15:45:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Username or email already exists
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Admin access required
- `404 Not Found`: User not found

**Notes**:
- Admins can promote users to admin status or demote admins to regular users
- Admins can update any user's username and email
- Username and email must still be unique across all users

### Delete User

Delete a user account (admin only).

**Endpoint**: `DELETE /admin/users/{user_id}`

**Headers**:
```
Authorization: Bearer <admin_access_token>
```

**Response** (204 No Content)

**Error Responses**:
- `400 Bad Request`: Cannot delete your own account
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Admin access required
- `404 Not Found`: User not found

**Notes**:
- Deleting a user will CASCADE delete all their data (medications, tags, logs, etc.)
- Admins cannot delete their own account
- This action is irreversible

## Error Responses

### Standard Error Format

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request succeeded |
| 201 | Created - Resource created successfully |
| 204 | No Content - Request succeeded, no response body |
| 400 | Bad Request - Invalid input data |
| 401 | Unauthorized - Missing or invalid authentication |
| 403 | Forbidden - Authenticated but not authorized |
| 404 | Not Found - Resource doesn't exist |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error - Server error |

### Validation Errors

Validation errors return detailed information about each field:

```json
{
  "detail": [
    {
      "loc": ["body", "drug_name"],
      "msg": "field required",
      "type": "value_error.missing"
    },
    {
      "loc": ["body", "color"],
      "msg": "color must be a valid hex color code (e.g., #FF5733)",
      "type": "value_error"
    }
  ]
}
```

## Data Models

### Medication

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Auto | Unique identifier |
| user_id | UUID | Auto | User who owns this medication |
| drug_name | string | Yes | Name of the medication |
| pharmacy | string | No | Pharmacy where medication is filled |
| prescription_type | enum | No | Type: `long_term`, `short_term`, `otc` (default: `long_term`) |
| dosing_schedule | object | No | Flexible JSONB object for dosing instructions |
| standard_dose | string | Yes | Standard dose amount (e.g., "10mg", "2 tablets") |
| date_prescribed | date | No | Date medication was prescribed |
| date_filled | date | No | Date prescription was filled |
| prescribing_doctor | string | No | Name of prescribing doctor |
| prescription_number | string | No | Prescription number |
| notes | text | No | Additional notes |
| active | boolean | No | Whether medication is active (default: true) |
| start_date | date | Yes | Date to start taking medication |
| end_date | date | No | Date to stop (for short-term medications) |
| tags | array[Tag] | No | Tags associated with this medication |
| created_at | datetime | Auto | When record was created |
| updated_at | datetime | Auto | When record was last updated |

### Tag

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Auto | Unique identifier |
| user_id | UUID | Auto | User who owns this tag |
| name | string | Yes | Tag name (1-100 chars, unique per user) |
| color | string | No | Hex color code (format: #RRGGBB) |
| created_at | datetime | Auto | When record was created |
| updated_at | datetime | Auto | When record was last updated |

### User

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Auto | Unique identifier |
| username | string | Yes | Username (unique) |
| email | string | Yes | Email address (unique) |
| password_hash | string | Internal | Bcrypt hashed password |
| created_at | datetime | Auto | When account was created |
| updated_at | datetime | Auto | When account was last updated |

## Examples

### Example: Create Medication Workflow

```bash
# 1. Register user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "secure123"
  }'

# 2. Login
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -d "username=john@example.com&password=secure123" \
  | jq -r '.access_token')

# 3. Create tags
TAG1=$(curl -X POST http://localhost:8000/api/tags/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Morning", "color": "#FF5733"}' \
  | jq -r '.id')

# 4. Create medication with tag
curl -X POST http://localhost:8000/api/medications/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"drug_name\": \"Lisinopril\",
    \"standard_dose\": \"10mg\",
    \"prescription_type\": \"long_term\",
    \"start_date\": \"2025-11-16\",
    \"tag_ids\": [\"$TAG1\"]
  }"

# 5. List medications filtered by tag
curl -X GET "http://localhost:8000/api/medications/?tag_ids=$TAG1" \
  -H "Authorization: Bearer $TOKEN"
```

## Rate Limiting

Currently, there are no rate limits enforced. This may change in future versions.

## Changelog

### Version 1.2.0 (2025-11-16)
- Added OAuth authentication support
- Google OAuth login and callback endpoints
- GitHub OAuth login and callback endpoints
- User model updated with oauth_provider and oauth_id fields
- Password field now optional for OAuth users
- Automatic account linking for existing users
- Enhanced login endpoint to detect and prevent OAuth/password conflicts

### Version 1.1.0 (2025-11-16)
- Added admin functionality
- Admin user management endpoints (list, view, update, delete users)
- Role-based access control with is_admin flag
- Admin authorization dependency

### Version 1.0.0 (2025-11-16)
- Initial API release
- Authentication endpoints
- Medication CRUD operations
- Tag management
- Medication-tag associations
- Filtering and pagination support
