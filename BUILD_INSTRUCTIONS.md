# MedTrack - Build Instructions

## Table of Contents
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Initial Setup](#initial-setup)
- [Development Build](#development-build)
- [Production Build](#production-build)
- [Database Setup](#database-setup)
- [Running Tests](#running-tests)
- [Troubleshooting](#troubleshooting)
- [Environment Variables](#environment-variables)

## Prerequisites

### Required Software

1. **Docker** (v20.10+)
   - macOS: [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
   - Linux: [Docker Engine](https://docs.docker.com/engine/install/)
   - Windows: [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)

2. **Docker Compose** (v2.0+)
   - Included with Docker Desktop
   - Linux: Install separately if needed

3. **Git**
   - macOS: `brew install git` or use Xcode Command Line Tools
   - Linux: `sudo apt-get install git` (Ubuntu/Debian)
   - Windows: [Git for Windows](https://git-scm.com/download/win)

### Recommended Tools

- **Node.js** (v18+) - For local frontend development
- **Python** (3.11+) - For local backend development
- **PyCharm** or **VS Code** - For development
- **Postman** or **Insomnia** - For API testing

## Project Structure

```
drug_tracker/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── utils/          # Utilities
│   ├── alembic/            # Database migrations
│   ├── tests/              # Test suite
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API services
│   │   └── styles/        # CSS styles
│   ├── package.json       # Node dependencies
│   └── Dockerfile
├── docker-compose.yml     # Docker orchestration
└── .env.example          # Environment template

```

## Initial Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd drug_tracker
```

### 2. Environment Configuration

Create environment files from templates:

```bash
# Copy example environment file
cp .env.example .env

# Edit with your values
nano .env  # or use your preferred editor
```

**Required Environment Variables:**

```env
# Database
POSTGRES_USER=medtrack_user
POSTGRES_PASSWORD=medtrack_dev_pass_2024
POSTGRES_DB=medtrack

# Backend
SECRET_KEY=your-secret-key-here-change-in-production
DATABASE_URL=postgresql://medtrack_user:medtrack_dev_pass_2024@postgres:5432/medtrack
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OAuth (Optional - for Google login)
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5173/auth/callback

# Frontend
VITE_API_URL=http://localhost:8000
```

### 3. Generate Secret Key

```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or use OpenSSL
openssl rand -hex 32
```

Add the generated key to your `.env` file as `SECRET_KEY`.

## Development Build

### Quick Start (Recommended)

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Step-by-Step Development Build

#### 1. Build Docker Images

```bash
# Build all services
docker-compose build

# Or build specific services
docker-compose build backend
docker-compose build frontend
```

#### 2. Start Services

```bash
# Start all services in background
docker-compose up -d

# Or start with logs visible
docker-compose up
```

#### 3. Verify Services

```bash
# Check running containers
docker-compose ps

# Expected output:
# NAME                  STATUS              PORTS
# medtrack_backend      Up                  0.0.0.0:8000->8000/tcp
# medtrack_frontend     Up                  0.0.0.0:5173->5173/tcp
# medtrack_postgres     Up                  0.0.0.0:5432->5432/tcp
```

#### 4. Access Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432

### Hot Reload Development

Both frontend and backend support hot reload:

```bash
# Backend changes automatically reload
# Edit files in backend/app/

# Frontend changes automatically reload
# Edit files in frontend/src/

# View backend logs
docker-compose logs -f backend

# View frontend logs
docker-compose logs -f frontend
```

## Production Build

### 1. Update Environment Variables

Create production `.env` file:

```env
# Use strong passwords
POSTGRES_PASSWORD=<strong-password>
SECRET_KEY=<strong-secret-key>

# Production database URL
DATABASE_URL=postgresql://medtrack_user:<password>@postgres:5432/medtrack

# Production API URL
VITE_API_URL=https://api.yourdomain.com

# Security settings
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### 2. Build Production Images

```bash
# Build with production settings
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Or use production-specific Dockerfiles
docker build -t medtrack-backend:prod ./backend
docker build -t medtrack-frontend:prod ./frontend
```

### 3. Deploy

```bash
# Start production stack
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps
```

### 4. SSL/TLS Setup (Recommended)

Use nginx or Caddy as reverse proxy:

```yaml
# docker-compose.prod.yml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
```

## Database Setup

### 1. Run Migrations

```bash
# Apply all migrations
docker-compose exec backend alembic upgrade head

# Check migration status
docker-compose exec backend alembic current

# Create new migration (if needed)
docker-compose exec backend alembic revision --autogenerate -m "description"
```

### 2. Create Admin User (Optional)

```bash
# Access backend shell
docker-compose exec backend python

# In Python shell:
from app.database import SessionLocal
from app.models.user import User
from app.utils.security import get_password_hash

db = SessionLocal()
admin = User(
    username="admin",
    email="admin@example.com",
    password_hash=get_password_hash("your-password"),
    is_admin=True
)
db.add(admin)
db.commit()
exit()
```

### 3. Database Backup

```bash
# Backup database
docker-compose exec postgres pg_dump -U medtrack_user medtrack > backup.sql

# Restore database
docker-compose exec -T postgres psql -U medtrack_user medtrack < backup.sql
```

### 4. Reset Database (Development Only)

```bash
# WARNING: This deletes all data
docker-compose down -v
docker-compose up -d
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
docker-compose exec backend pytest tests/integration/test_api_medications.py

# Run unit tests only
docker-compose exec backend pytest tests/unit/ -v

# Run integration tests only
docker-compose exec backend pytest tests/integration/ -v
```

### Frontend Tests (if configured)

```bash
# Run frontend tests
docker-compose exec frontend npm test

# Run with coverage
docker-compose exec frontend npm test -- --coverage
```

## Troubleshooting

### Port Already in Use

```bash
# Check what's using the port
lsof -i :8000  # Backend
lsof -i :5173  # Frontend
lsof -i :5432  # Database

# Kill the process
kill -9 <PID>

# Or change ports in docker-compose.yml
```

### Container Won't Start

```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres

# Rebuild without cache
docker-compose build --no-cache

# Remove all containers and volumes
docker-compose down -v
docker-compose up -d
```

### Database Connection Issues

```bash
# Check if database is ready
docker-compose exec postgres pg_isready

# Check database logs
docker-compose logs postgres

# Access database directly
docker-compose exec postgres psql -U medtrack_user -d medtrack

# Test connection from backend
docker-compose exec backend python -c "from app.database import engine; print(engine.connect())"
```

### Permission Issues

```bash
# Fix file permissions (Linux/macOS)
sudo chown -R $USER:$USER .

# Fix Docker socket permissions (Linux)
sudo usermod -aG docker $USER
newgrp docker
```

### Frontend Build Errors

```bash
# Clear node modules and rebuild
docker-compose exec frontend rm -rf node_modules package-lock.json
docker-compose exec frontend npm install

# Or rebuild container
docker-compose build --no-cache frontend
```

### Backend Dependencies Issues

```bash
# Rebuild with updated dependencies
docker-compose exec backend pip install -r requirements.txt --no-cache-dir

# Or rebuild container
docker-compose build --no-cache backend
```

### Migration Issues

```bash
# Check current migration
docker-compose exec backend alembic current

# View migration history
docker-compose exec backend alembic history

# Downgrade one migration
docker-compose exec backend alembic downgrade -1

# Upgrade to specific version
docker-compose exec backend alembic upgrade <revision>
```

## Local Development (Without Docker)

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set environment variables
export DATABASE_URL=postgresql://user:pass@localhost:5432/medtrack
export SECRET_KEY=your-secret-key

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Set environment variables
export VITE_API_URL=http://localhost:8000

# Start development server
npm run dev

# Build for production
npm run build
```

## Environment Variables

### Backend Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | - | Yes |
| `SECRET_KEY` | JWT secret key | - | Yes |
| `ALGORITHM` | JWT algorithm | HS256 | No |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | 30 | No |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | - | No |
| `GOOGLE_CLIENT_SECRET` | Google OAuth secret | - | No |

### Frontend Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `VITE_API_URL` | Backend API URL | http://localhost:8000 | Yes |

## Performance Optimization

### Backend

```bash
# Use gunicorn with multiple workers (production)
docker-compose exec backend gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Frontend

```bash
# Build with optimization
docker-compose exec frontend npm run build

# Analyze bundle size
docker-compose exec frontend npm run build -- --analyze
```

### Database

```bash
# Create indexes (if needed)
docker-compose exec postgres psql -U medtrack_user -d medtrack -c \
  "CREATE INDEX idx_medications_user_id ON medications(user_id);"

# Analyze database
docker-compose exec postgres psql -U medtrack_user -d medtrack -c "ANALYZE;"
```

## Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Database health
docker-compose exec postgres pg_isready

# Check all services
docker-compose ps
```

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Save logs to file
docker-compose logs > logs.txt
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Test

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Build containers
      run: docker-compose build

    - name: Start services
      run: docker-compose up -d

    - name: Run tests
      run: docker-compose exec -T backend pytest

    - name: Stop services
      run: docker-compose down
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

## Getting Help

- Check logs: `docker-compose logs`
- Review environment variables
- Verify port availability
- Check Docker daemon status
- Consult documentation above

---

**Last Updated**: 2025-11-18
**Version**: 1.0.0
