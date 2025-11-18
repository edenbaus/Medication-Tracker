# Medication Tracker

A comprehensive medication tracking application that allows users to manage prescriptions, log medication intake, track side effects, and monitor symptom improvements.

## Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL
- **Frontend**: React 18 with Vite
- **Containerization**: Docker + Docker Compose
- **Testing**: pytest, Vitest, Playwright

## Project Status

✅ **Phase 1: Project Setup & Foundation - COMPLETED**
✅ **Phase 2: Core Medication Management - COMPLETED**
✅ **Phase 3: Logging System - COMPLETED**
✅ **Phase 4: Side Effects & Symptom Tracking - COMPLETED**

### Completed Features

- [x] User authentication (JWT + Google OAuth)
- [x] Medication CRUD with prescriptions
- [x] Tag system for organizing medications
- [x] Medication logging and tracking
- [x] Third-party management (family members, others)
- [x] Regimens for medication groups
- [x] Side effects reporting and tracking
- [x] Symptom monitoring with improvement levels
- [x] **Usage analytics with Chart.js visualizations**
- [x] **Adherence statistics**
- [x] **Symptom trend analysis**
- [x] Admin functionality
- [x] All timestamps in US Eastern timezone

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js 20+ (for local development without Docker)
- Python 3.11+ (for local development without Docker)

### Quick Start with Docker

1. Clone the repository:
```bash
git clone <repository-url>
cd drug_tracker
```

2. Copy the environment file and adjust if needed:
```bash
cp .env.example .env
```

3. Start the services:
```bash
docker-compose up --build
```

4. The application will be available at:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

5. Run database migrations:
```bash
docker-compose exec backend alembic upgrade head
```

## Running Tests

### Backend Tests

```bash
# Run all tests
docker-compose exec backend pytest

# Run with coverage
docker-compose exec backend pytest --cov=app --cov-report=html

# Run specific test file
docker-compose exec backend pytest tests/integration/test_api_auth.py

# Run unit tests only
docker-compose exec backend pytest tests/unit/
```

### Frontend Tests

```bash
# Run unit tests
cd frontend && npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch

# Run E2E tests
npm run test:e2e
```

## Project Structure

```
drug_tracker/
├── backend/
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── models/        # Database models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   └── utils/         # Utilities
│   ├── alembic/           # Database migrations
│   └── tests/             # Backend tests
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API services
│   │   └── utils/         # Utilities
│   └── tests/             # Frontend tests
└── docker-compose.yml     # Docker services
```

## Development

### Backend Development

The backend is built with FastAPI and follows a clean architecture pattern:

- **Models**: SQLAlchemy ORM models
- **Schemas**: Pydantic models for validation
- **API Routes**: FastAPI endpoints
- **Services**: Business logic layer
- **Utils**: Helper functions and utilities

### Frontend Development

The frontend uses React 18 with modern hooks and follows these principles:

- Component-based architecture
- Service layer for API calls
- React Router for navigation
- Axios for HTTP requests

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation powered by Swagger/OpenAPI.

## Environment Variables

See `.env.example` for all available environment variables. Key variables:

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key
- `VITE_API_URL`: Backend API URL for frontend

## Key Features

### Medication Management
- Add, edit, and delete medications
- Track long-term, short-term, and OTC medications
- Organize with custom colored tags
- Assign to family members or third parties
- Group into regimens

### Tracking & Logging
- Quick medication logging
- View log history with filters
- Track adherence with statistics
- Report side effects (mild, moderate, severe)
- Monitor symptom improvements (1-10 scale)

### Analytics & Visualizations
- Interactive usage charts (daily/weekly)
- Adherence percentage tracking
- Symptom trend analysis
- All data visualized with Chart.js

### User Experience
- Google OAuth login
- Responsive design (mobile, tablet, desktop)
- US Eastern timezone for all timestamps
- Real-time updates
- Comprehensive error handling

## Next Steps

**Phase 5**: Advanced Analytics & Reporting
- Enhanced trend visualizations
- Export functionality (CSV, PDF)
- Medication reports for doctors
- Advanced filtering and search

**Phase 6**: Comprehensive Testing
- Integration tests for all APIs
- Frontend component tests
- E2E test suites
- Performance testing

## Contributing

This is a personal project. For any questions or suggestions, please open an issue.

## License

Private project - All rights reserved.
