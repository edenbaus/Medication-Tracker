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

- [x] Git repository initialized
- [x] Project directory structure created
- [x] Docker and Docker Compose configured
- [x] FastAPI project structure set up
- [x] PostgreSQL database models created (User model)
- [x] Alembic for database migrations configured
- [x] JWT authentication implemented
- [x] Environment configuration files created
- [x] pytest with coverage reporting configured
- [x] Test database fixtures set up
- [x] React frontend initialized with Vite
- [x] Vitest for frontend testing configured
- [x] Playwright for e2e tests set up
- [x] First authentication tests written

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

## Next Steps (Phase 2)

- Implement medication CRUD endpoints
- Create medication database models
- Build medication management UI
- Implement tag system for medication organization
- Add medication list views with filtering

## Contributing

This is a personal project. For any questions or suggestions, please open an issue.

## License

Private project - All rights reserved.
