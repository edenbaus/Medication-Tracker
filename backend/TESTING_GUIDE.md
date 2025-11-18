# MedTrack Testing Guide

## Overview

This document provides comprehensive guidance on the testing suite for the MedTrack application. The test suite includes unit tests, integration tests, and fixtures for all major components.

## Test Structure

```
backend/tests/
├── conftest.py                 # Global fixtures and configuration
├── factories/
│   └── factories.py           # Test data factories
├── unit/
│   ├── test_dashboard.py      # Dashboard logic unit tests
│   ├── test_models.py         # Model validation tests
│   ├── test_security.py       # Security utilities tests
│   └── test_utils.py          # Utility function tests
├── integration/
│   ├── test_api_admin.py      # Admin endpoint tests
│   ├── test_api_auth.py       # Authentication tests
│   ├── test_api_dashboard.py  # Dashboard API tests
│   ├── test_api_journey.py    # Journey visualization tests
│   ├── test_api_logs.py       # Medication logs tests
│   ├── test_api_medications.py # Medications endpoint tests
│   ├── test_api_regimens.py   # Regimens tests
│   ├── test_api_side_effects.py # Side effects tests
│   ├── test_api_symptoms.py   # Symptoms tracking tests
│   ├── test_api_tags.py       # Tags tests
│   └── test_api_third_parties.py # Third parties tests
├── performance/               # Performance tests (future)
└── e2e/                      # End-to-end tests (future)
```

## Running Tests

### Run All Tests
```bash
# From backend directory
docker-compose exec backend pytest

# Or from project root
docker-compose exec backend pytest tests/
```

### Run Specific Test Categories

```bash
# Run only unit tests
docker-compose exec backend pytest tests/unit/ -v

# Run only integration tests
docker-compose exec backend pytest tests/integration/ -v

# Run tests with markers
docker-compose exec backend pytest -m "unit" -v
docker-compose exec backend pytest -m "integration" -v
docker-compose exec backend pytest -m "api" -v
```

### Run Specific Test Files
```bash
# Run specific test file
docker-compose exec backend pytest tests/integration/test_api_medications.py -v

# Run specific test class
docker-compose exec backend pytest tests/integration/test_api_medications.py::TestMedicationsAPI -v

# Run specific test
docker-compose exec backend pytest tests/integration/test_api_medications.py::TestMedicationsAPI::test_create_medication -v
```

### Run Tests with Coverage
```bash
# Run with coverage report
docker-compose exec backend pytest --cov=app --cov-report=html

# View coverage report
open backend/htmlcov/index.html  # macOS
xdg-open backend/htmlcov/index.html  # Linux
```

### Run Tests in PyCharm

1. **Configure Python Interpreter:**
   - File → Settings → Project → Python Interpreter
   - Select Docker Compose interpreter
   - Choose the backend service

2. **Configure pytest:**
   - File → Settings → Tools → Python Integrated Tools
   - Set Default test runner to "pytest"
   - Set pytest options: `-v --tb=short`

3. **Run Tests:**
   - Right-click on `tests/` directory → Run 'pytest in tests'
   - Right-click on individual test file → Run 'pytest in...'
   - Right-click on test class/function → Run

4. **Run with Coverage:**
   - Run → Run with Coverage
   - Or use keyboard shortcut (varies by OS)

## Test Fixtures

### Database Fixtures

- **`db_session`**: Fresh database session for each test
- **`client`**: FastAPI test client with database override

### User Fixtures

- **`test_user`**: Standard test user
- **`admin_user`**: Admin user for testing admin endpoints
- **`auth_headers`**: Authentication headers for test user
- **`admin_headers`**: Authentication headers for admin user

### Model Fixtures

- **`test_medication`**: Sample medication
- **`test_medication_log`**: Sample medication log
- **`test_side_effect`**: Sample side effect
- **`test_symptom`**: Sample symptom tracking
- **`test_tag`**: Sample tag
- **`test_third_party`**: Sample third party
- **`test_regimen`**: Sample regimen

## Test Factories

Located in `tests/factories/factories.py`, factories provide an easy way to create test data:

```python
from tests.factories.factories import (
    UserFactory,
    MedicationFactory,
    MedicationLogFactory,
    SideEffectFactory,
    SymptomFactory,
    TagFactory,
    ThirdPartyFactory,
    RegimenFactory,
)

# Example usage in tests
def test_something(db_session):
    user = UserFactory.create(db_session, email="test@example.com")
    medication = MedicationFactory.create(db_session, user, drug_name="Aspirin")
    log = MedicationLogFactory.create(db_session, medication)
```

## Test Markers

Tests are organized using pytest markers:

- **`@pytest.mark.unit`**: Fast, isolated unit tests
- **`@pytest.mark.integration`**: Tests with database/external services
- **`@pytest.mark.slow`**: Long-running tests
- **`@pytest.mark.auth`**: Authentication/authorization tests
- **`@pytest.mark.api`**: API endpoint tests
- **`@pytest.mark.models`**: Model validation tests
- **`@pytest.mark.security`**: Security-related tests

Example:
```python
@pytest.mark.integration
@pytest.mark.api
def test_create_medication(client, auth_headers):
    # Test implementation
    pass
```

## Test Coverage Goals

- **Overall Coverage**: 85% minimum
- **Models**: 100%
- **Schemas**: 100%
- **API Endpoints**: 90%+
- **Utilities**: 95%+

## Writing New Tests

### Unit Test Template
```python
"""Unit tests for [component]."""
import pytest


class Test[Component]:
    """Test [component] functionality."""

    def test_[specific_functionality](self):
        """Test [what it does]."""
        # Arrange
        # ... setup test data

        # Act
        # ... execute the code being tested

        # Assert
        # ... verify expected results
        assert result == expected
```

### Integration Test Template
```python
"""Integration tests for [endpoint] API."""
import pytest


class Test[Endpoint]API:
    """Test [endpoint] API endpoints."""

    def test_create_[resource](self, client, auth_headers):
        """Test creating a [resource]."""
        data = {
            "field": "value"
        }

        response = client.post("/api/[endpoint]", json=data, headers=auth_headers)

        assert response.status_code == 201
        result = response.json()
        assert result["field"] == "value"

    def test_unauthorized_access(self, client):
        """Test accessing [endpoint] without authentication."""
        response = client.get("/api/[endpoint]")
        assert response.status_code == 401
```

## Common Testing Patterns

### Testing Authentication
```python
def test_requires_auth(client):
    """Test endpoint requires authentication."""
    response = client.get("/api/protected-endpoint")
    assert response.status_code == 401
```

### Testing Authorization
```python
def test_requires_admin(client, auth_headers):
    """Test endpoint requires admin access."""
    response = client.get("/api/admin-endpoint", headers=auth_headers)
    assert response.status_code == 403
```

### Testing Data Isolation
```python
def test_user_data_isolation(client, auth_headers, db_session):
    """Test users can only access their own data."""
    # Create another user's data
    other_user = UserFactory.create(db_session, email="other@example.com")
    other_medication = MedicationFactory.create(db_session, other_user)

    # Try to access it
    response = client.get(f"/api/medications/{other_medication.id}", headers=auth_headers)
    assert response.status_code == 404
```

### Testing Validation
```python
def test_invalid_input(client, auth_headers):
    """Test validation rejects invalid input."""
    data = {
        "field": "invalid_value"
    }

    response = client.post("/api/endpoint", json=data, headers=auth_headers)
    assert response.status_code == 422
```

## Continuous Integration

### GitHub Actions (Example)
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Run tests
      run: |
        docker-compose up -d
        docker-compose exec -T backend pytest --cov=app --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        file: ./backend/coverage.xml
```

## Troubleshooting

### Tests Failing Due to Database State
```bash
# Reset database
docker-compose down -v
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

### Tests Running Slowly
```bash
# Run only fast tests
docker-compose exec backend pytest -m "not slow"

# Run with multiple workers (requires pytest-xdist)
docker-compose exec backend pytest -n auto
```

### Coverage Not Updating
```bash
# Clear coverage cache
rm -rf backend/.coverage backend/htmlcov

# Re-run with fresh coverage
docker-compose exec backend pytest --cov=app --cov-report=html
```

## Best Practices

1. **Use Factories**: Always use factories instead of creating objects manually
2. **Descriptive Names**: Test names should describe what they test
3. **One Assertion per Test**: Focus each test on one specific behavior
4. **Arrange-Act-Assert**: Follow the AAA pattern
5. **Clean Up**: Use fixtures and transactions for automatic cleanup
6. **Test Isolation**: Tests should not depend on each other
7. **Mock External Services**: Don't make real API calls or send emails
8. **Test Edge Cases**: Include tests for boundary conditions
9. **Document**: Add docstrings explaining what the test validates
10. **Keep Tests Fast**: Unit tests should run in milliseconds

## Test Coverage Report

Current coverage (as of last run):
- **Total Lines**: 1,810
- **Covered Lines**: ~970
- **Coverage**: 53.56%

### Priority Areas for Improvement:
1. API endpoint coverage (currently 30-40%)
2. OAuth authentication flows
3. Journey visualization logic
4. Complex business logic in models

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
- [Test-Driven Development](https://en.wikipedia.org/wiki/Test-driven_development)

---

**Last Updated**: 2025-11-18
