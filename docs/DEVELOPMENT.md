# Development Guide

## Table of Contents

- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Database Management](#database-management)
- [Code Style](#code-style)
- [Adding New Features](#adding-new-features)
- [Debugging](#debugging)
- [Common Tasks](#common-tasks)

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git
- Text editor or IDE (VS Code, PyCharm, etc.)

### Initial Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd drug_tracker
   ```

2. **Create environment file**:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set your values:
   ```env
   DB_PASSWORD=your_secure_password
   SECRET_KEY=your_secret_key_for_jwt
   ENVIRONMENT=development
   DEBUG=True
   VITE_API_URL=http://localhost:8000
   ```

3. **Start services**:
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations**:
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

5. **Verify setup**:
   ```bash
   # Check backend health
   curl http://localhost:8000/health

   # Check API documentation
   open http://localhost:8000/docs
   ```

### Development Environment

**Backend** runs on: `http://localhost:8000`
**Frontend** runs on: `http://localhost:5173`
**PostgreSQL** runs on: `localhost:5432`

## Project Structure

```
drug_tracker/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py           # Shared dependencies (auth, db)
│   │   │   └── v1/
│   │   │       ├── auth.py       # Authentication endpoints
│   │   │       ├── medications.py # Medication endpoints
│   │   │       └── tags.py       # Tag endpoints
│   │   ├── models/                # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── medication.py
│   │   │   ├── tag.py
│   │   │   ├── medication_log.py
│   │   │   ├── side_effect.py
│   │   │   └── symptom.py
│   │   ├── schemas/               # Pydantic schemas
│   │   │   ├── user.py
│   │   │   ├── medication.py
│   │   │   └── tag.py
│   │   ├── utils/
│   │   │   └── security.py       # Password hashing, JWT
│   │   ├── config.py             # App configuration
│   │   ├── database.py           # Database connection
│   │   └── main.py               # FastAPI app
│   ├── alembic/                   # Database migrations
│   │   └── versions/
│   ├── tests/
│   │   ├── conftest.py           # Test fixtures
│   │   ├── unit/                 # Unit tests
│   │   └── integration/          # Integration tests
│   ├── requirements.txt          # Python dependencies
│   ├── requirements-dev.txt      # Development dependencies
│   ├── pytest.ini               # Pytest configuration
│   └── Dockerfile
├── frontend/                      # React application
├── docs/                          # Documentation
│   ├── API.md                    # API documentation
│   ├── TESTING.md               # Testing guide
│   └── DEVELOPMENT.md           # This file
├── docker-compose.yml
└── .env
```

### Key Files

- **`backend/app/main.py`** - FastAPI application entry point
- **`backend/app/config.py`** - Configuration and environment variables
- **`backend/app/database.py`** - Database connection and session management
- **`backend/alembic/env.py`** - Alembic migration configuration
- **`docker-compose.yml`** - Docker services configuration

## Development Workflow

### Daily Development

1. **Start services** (if not running):
   ```bash
   docker-compose up -d
   ```

2. **Check logs**:
   ```bash
   # Backend logs
   docker-compose logs -f backend

   # All logs
   docker-compose logs -f
   ```

3. **Make code changes**:
   - Backend code auto-reloads on changes (uvicorn --reload)
   - Frontend code auto-reloads on changes (Vite HMR)

4. **Run tests**:
   ```bash
   docker-compose exec backend pytest
   ```

5. **Commit changes**:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push
   ```

### Hot Reload

Both backend and frontend support hot reload:

- **Backend**: Uvicorn automatically reloads when Python files change
- **Frontend**: Vite Hot Module Replacement (HMR) updates browser instantly

### Stopping Services

```bash
# Stop services
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes (deletes database!)
docker-compose down -v
```

## Database Management

### Migrations

We use Alembic for database migrations.

#### Create a New Migration

After modifying models in `app/models/`:

```bash
# Auto-generate migration from model changes
docker-compose exec backend alembic revision --autogenerate -m "description"

# Example
docker-compose exec backend alembic revision --autogenerate -m "add refill tracking to medications"
```

#### Review Migration

**Always review** the generated migration file in `backend/alembic/versions/`:

```python
# Example: alembic/versions/003_add_refill_tracking.py
def upgrade() -> None:
    op.add_column('medications', sa.Column('refills_remaining', sa.Integer(), nullable=True))

def downgrade() -> None:
    op.drop_column('medications', 'refills_remaining')
```

#### Apply Migrations

```bash
# Apply all pending migrations
docker-compose exec backend alembic upgrade head

# Apply specific migration
docker-compose exec backend alembic upgrade <revision_id>

# Rollback one migration
docker-compose exec backend alembic downgrade -1

# Rollback to specific revision
docker-compose exec backend alembic downgrade <revision_id>
```

#### Migration History

```bash
# View migration history
docker-compose exec backend alembic history

# View current version
docker-compose exec backend alembic current
```

### Database Access

#### psql Shell

```bash
docker-compose exec postgres psql -U medtrack_user -d medtrack
```

Useful psql commands:
```sql
-- List all tables
\dt

-- Describe table structure
\d medications

-- List all databases
\l

-- Quit
\q
```

#### Database Backup

```bash
# Create backup
docker-compose exec postgres pg_dump -U medtrack_user medtrack > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U medtrack_user medtrack < backup.sql
```

#### Reset Database

**Warning**: This will delete all data!

```bash
# Drop and recreate database
docker-compose exec postgres psql -U medtrack_user -d postgres -c "DROP DATABASE medtrack;"
docker-compose exec postgres psql -U medtrack_user -d postgres -c "CREATE DATABASE medtrack;"

# Run migrations
docker-compose exec backend alembic upgrade head
```

## Code Style

### Python (Backend)

We follow PEP 8 with some modifications.

#### Linting and Formatting

```bash
# Check code style
docker-compose exec backend ruff check app/

# Auto-fix issues
docker-compose exec backend ruff check --fix app/

# Format code with Black
docker-compose exec backend black app/

# Type checking with mypy
docker-compose exec backend mypy app/
```

#### Style Guidelines

**Imports**:
```python
# Standard library
import os
import sys
from datetime import datetime

# Third-party
from fastapi import FastAPI, Depends
from sqlalchemy import Column, String

# Local
from app.models import User
from app.utils.security import get_password_hash
```

**Function Docstrings**:
```python
def create_medication(
    medication_in: MedicationCreate,
    current_user: User,
    db: Session
) -> Medication:
    """
    Create a new medication for the current user.

    Args:
        medication_in: Medication data from request
        current_user: Authenticated user
        db: Database session

    Returns:
        Created medication object

    Raises:
        HTTPException: If tag validation fails
    """
    pass
```

**Type Hints**:
```python
# Always use type hints
def get_medication_by_id(medication_id: UUID, db: Session) -> Optional[Medication]:
    return db.query(Medication).filter(Medication.id == medication_id).first()
```

### JavaScript/React (Frontend)

Follow Airbnb JavaScript Style Guide.

```bash
# Lint
cd frontend
npm run lint

# Format
npm run format

# Fix issues
npm run lint:fix
```

## Adding New Features

### Adding a New Model

1. **Create the model** (`app/models/new_feature.py`):
   ```python
   from sqlalchemy import Column, String, ForeignKey
   from sqlalchemy.dialects.postgresql import UUID
   from sqlalchemy.orm import relationship
   import uuid
   from app.database import Base

   class NewFeature(Base):
       __tablename__ = "new_features"

       id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
       user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
       name = Column(String, nullable=False)

       user = relationship("User", back_populates="new_features")
   ```

2. **Update user model** to add relationship
3. **Export from `__init__.py`**
4. **Create Pydantic schemas** (`app/schemas/new_feature.py`)
5. **Create migration**:
   ```bash
   docker-compose exec backend alembic revision --autogenerate -m "add new feature model"
   ```
6. **Review and apply migration**
7. **Write model tests** (`tests/unit/test_models.py`)

### Adding a New API Endpoint

1. **Create router** (`app/api/v1/new_feature.py`):
   ```python
   from fastapi import APIRouter, Depends
   from sqlalchemy.orm import Session
   from app.database import get_db
   from app.api.deps import get_current_user

   router = APIRouter()

   @router.get("/")
   def get_features(
       current_user: User = Depends(get_current_user),
       db: Session = Depends(get_db)
   ):
       """Get all features for current user."""
       features = db.query(NewFeature).filter(
           NewFeature.user_id == current_user.id
       ).all()
       return features
   ```

2. **Register router** in `app/main.py`:
   ```python
   from app.api.v1 import auth, medications, tags, new_feature

   app.include_router(new_feature.router, prefix="/api/new-features", tags=["Features"])
   ```

3. **Write integration tests** (`tests/integration/test_api_new_feature.py`)
4. **Update API documentation**
5. **Test endpoints**:
   ```bash
   # Via Swagger UI
   open http://localhost:8000/docs

   # Via curl
   curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/new-features/
   ```

### Adding a New Schema Validator

```python
from pydantic import BaseModel, Field, field_validator

class NewFeatureCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    value: int = Field(..., ge=0, le=100)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v.strip() != v:
            raise ValueError('name cannot have leading/trailing whitespace')
        return v.strip()
```

## Debugging

### Backend Debugging

#### Using Print Statements

```python
print(f"Debug: user_id={current_user.id}")  # Visible in docker-compose logs
```

#### Using Python Debugger (pdb)

Add breakpoint in code:
```python
import pdb; pdb.set_trace()
```

Then attach to container:
```bash
docker attach medtrack_backend
```

#### Checking Logs

```bash
# Real-time logs
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend

# Search logs
docker-compose logs backend | grep ERROR
```

#### Database Query Debugging

Enable SQLAlchemy query logging in `app/database.py`:
```python
engine = create_engine(settings.DATABASE_URL, echo=True)  # Shows all SQL queries
```

### Frontend Debugging

#### React DevTools

Install React Developer Tools browser extension.

#### Console Logging

```javascript
console.log('Debug:', data);
console.error('Error:', error);
console.table(arrayData);
```

#### Network Debugging

Use browser DevTools Network tab to inspect API calls.

### Testing Specific Scenarios

```bash
# Test with different user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser2", "email": "test2@example.com", "password": "test123"}'

# Get token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -d "username=test2@example.com&password=test123" | jq -r '.access_token')

# Make authenticated request
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/medications/
```

## Common Tasks

### Rebuild Containers

After changing dependencies or Dockerfile:

```bash
docker-compose build
docker-compose up -d
```

### Clear Python Cache

```bash
docker-compose exec backend find . -type d -name __pycache__ -exec rm -r {} +
docker-compose exec backend find . -type f -name "*.pyc" -delete
```

### Update Dependencies

**Backend**:
```bash
# Add new dependency
echo "new-package==1.0.0" >> backend/requirements.txt

# Rebuild
docker-compose build backend
docker-compose up -d backend
```

**Frontend**:
```bash
cd frontend
npm install new-package
```

### Run Code Quality Checks

```bash
# Backend
docker-compose exec backend ruff check app/
docker-compose exec backend black --check app/
docker-compose exec backend mypy app/
docker-compose exec backend pytest --cov=app

# Frontend
cd frontend
npm run lint
npm run format:check
npm test
```

### Create Test User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "devuser",
    "email": "dev@example.com",
    "password": "devpass123"
  }'
```

### Inspect Database State

```bash
# Open psql
docker-compose exec postgres psql -U medtrack_user -d medtrack

# Count records
SELECT 'users' as table_name, COUNT(*) FROM users
UNION ALL
SELECT 'medications', COUNT(*) FROM medications
UNION ALL
SELECT 'tags', COUNT(*) FROM tags;

# View recent medications
SELECT id, drug_name, prescription_type, active, created_at
FROM medications
ORDER BY created_at DESC
LIMIT 10;
```

### Monitor Performance

```bash
# Check container stats
docker stats medtrack_backend medtrack_postgres

# Check database connections
docker-compose exec postgres psql -U medtrack_user -d medtrack -c \
  "SELECT count(*) FROM pg_stat_activity WHERE datname='medtrack';"
```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Migration Conflicts

```bash
# Check current version
docker-compose exec backend alembic current

# Downgrade to previous version
docker-compose exec backend alembic downgrade -1

# Re-generate migration
docker-compose exec backend alembic revision --autogenerate -m "fix migration"
```

### Tests Failing

```bash
# Run single failing test for details
docker-compose exec backend pytest tests/path/to/test.py::test_name -v

# Clear test cache
docker-compose exec backend pytest --cache-clear

# Reset test database
docker-compose exec backend alembic downgrade base
docker-compose exec backend alembic upgrade head
```

## Best Practices

1. **Always write tests** for new features
2. **Run tests before committing**
3. **Keep migrations small and focused**
4. **Review migration files** before applying
5. **Use meaningful commit messages**
6. **Document complex logic**
7. **Keep dependencies up to date**
8. **Never commit secrets** to git
9. **Use environment variables** for configuration
10. **Follow the project structure** conventions

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## Getting Help

- Check the [API Documentation](./API.md)
- Check the [Testing Guide](./TESTING.md)
- Review existing code for examples
- Check FastAPI auto-generated docs: http://localhost:8000/docs
- Search project issues on GitHub

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.
