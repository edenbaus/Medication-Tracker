# Testing Guide

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [Writing Tests](#writing-tests)
- [Testing Best Practices](#testing-best-practices)
- [Continuous Integration](#continuous-integration)

## Overview

The Medication Tracker project follows a comprehensive testing strategy with three layers of tests:

1. **Unit Tests** - Test individual components in isolation
2. **Integration Tests** - Test API endpoints and database interactions
3. **End-to-End Tests** - Test complete user workflows (future)

### Current Test Statistics

- **Total Tests**: 73
- **Test Coverage**: 96.49%
- **Test Execution Time**: ~20 seconds

## Test Structure

```
backend/tests/
├── conftest.py              # Pytest configuration and fixtures
├── unit/                    # Unit tests
│   ├── __init__.py
│   ├── test_models.py       # Database model tests
│   └── test_utils.py        # Utility function tests
└── integration/             # Integration tests
    ├── __init__.py
    ├── test_api_auth.py     # Authentication endpoint tests
    ├── test_api_medications.py  # Medication endpoint tests
    └── test_api_tags.py     # Tag endpoint tests
```

## Running Tests

### Prerequisites

Ensure Docker services are running:

```bash
docker-compose up -d
```

### Run All Tests

```bash
docker-compose exec backend pytest
```

### Run Specific Test Categories

**Unit Tests Only**:
```bash
docker-compose exec backend pytest tests/unit/
```

**Integration Tests Only**:
```bash
docker-compose exec backend pytest tests/integration/
```

**Specific Test File**:
```bash
docker-compose exec backend pytest tests/unit/test_models.py
```

**Specific Test Class**:
```bash
docker-compose exec backend pytest tests/unit/test_models.py::TestMedicationModel
```

**Specific Test Function**:
```bash
docker-compose exec backend pytest tests/unit/test_models.py::TestMedicationModel::test_medication_creation
```

### Run Tests with Verbose Output

```bash
docker-compose exec backend pytest -v
```

### Run Tests with Coverage Report

```bash
docker-compose exec backend pytest --cov=app --cov-report=html
```

View the HTML coverage report:
```bash
open backend/htmlcov/index.html  # macOS
xdg-open backend/htmlcov/index.html  # Linux
```

### Run Tests Matching a Pattern

```bash
# Run all tests with "medication" in the name
docker-compose exec backend pytest -k medication

# Run all tests with "tag" in the name
docker-compose exec backend pytest -k tag
```

### Stop on First Failure

```bash
docker-compose exec backend pytest -x
```

### Show Test Duration

```bash
docker-compose exec backend pytest --durations=10
```

## Test Coverage

### Coverage Requirements

The project enforces a minimum test coverage of **85%** in `pytest.ini`.

### Current Coverage Breakdown

| Component | Coverage | Target |
|-----------|----------|--------|
| Models | 100% | 100% |
| Schemas | 96%+ | 95% |
| API Endpoints | 93-100% | 90% |
| Utils | 100% | 95% |
| **Overall** | **96.49%** | **85%** |

### Viewing Coverage Reports

**Terminal Report**:
```bash
docker-compose exec backend pytest --cov=app --cov-report=term-missing
```

**HTML Report** (detailed):
```bash
docker-compose exec backend pytest --cov=app --cov-report=html
```

**JSON Report** (for CI/CD):
```bash
docker-compose exec backend pytest --cov=app --cov-report=json
```

## Writing Tests

### Test Fixtures

Common fixtures are defined in `tests/conftest.py`:

#### `db_session`

Provides a clean database session for each test with transaction rollback.

```python
def test_create_tag(db_session, test_user):
    tag = Tag(user_id=test_user.id, name="Test Tag")
    db_session.add(tag)
    db_session.commit()

    assert tag.id is not None
```

#### `client`

Provides a FastAPI test client.

```python
def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
```

#### `test_user`

Creates a test user in the database.

```python
def test_user_has_medications(test_user):
    assert test_user.username == "testuser"
    assert test_user.email == "test@example.com"
```

#### `auth_headers`

Provides authentication headers with a valid JWT token.

```python
def test_get_medications(client, auth_headers):
    response = client.get("/api/medications/", headers=auth_headers)
    assert response.status_code == 200
```

### Unit Test Examples

#### Testing Models

```python
from app.models import Medication, Tag, PrescriptionType
from datetime import date

def test_medication_creation(db_session, test_user):
    """Test creating a medication."""
    medication = Medication(
        user_id=test_user.id,
        drug_name="Aspirin",
        standard_dose="100mg",
        prescription_type=PrescriptionType.OTC,
        start_date=date.today()
    )
    db_session.add(medication)
    db_session.commit()

    assert medication.id is not None
    assert medication.drug_name == "Aspirin"
    assert medication.active is True
```

#### Testing Relationships

```python
def test_medication_with_tags(db_session, test_user):
    """Test many-to-many relationship between medications and tags."""
    medication = Medication(
        user_id=test_user.id,
        drug_name="Lisinopril",
        standard_dose="10mg",
        start_date=date.today()
    )
    tag1 = Tag(user_id=test_user.id, name="Morning")
    tag2 = Tag(user_id=test_user.id, name="Heart Health")

    medication.tags.extend([tag1, tag2])
    db_session.add(medication)
    db_session.commit()

    assert len(medication.tags) == 2
    assert tag1 in medication.tags
```

#### Testing Constraints

```python
import pytest

def test_tag_unique_constraint(db_session, test_user):
    """Test that tag names must be unique per user."""
    tag1 = Tag(user_id=test_user.id, name="Daily")
    db_session.add(tag1)
    db_session.commit()

    # Try to create duplicate
    tag2 = Tag(user_id=test_user.id, name="Daily")
    db_session.add(tag2)

    with pytest.raises(Exception):  # IntegrityError
        db_session.commit()
```

### Integration Test Examples

#### Testing API Endpoints

```python
def test_create_medication(client, auth_headers):
    """Test creating a medication via API."""
    response = client.post(
        "/api/medications/",
        headers=auth_headers,
        json={
            "drug_name": "Aspirin",
            "standard_dose": "100mg",
            "prescription_type": "otc",
            "start_date": str(date.today())
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["drug_name"] == "Aspirin"
    assert "id" in data
```

#### Testing Authorization

```python
def test_medication_requires_auth(client):
    """Test that endpoint requires authentication."""
    response = client.get("/api/medications/")
    assert response.status_code == 401
```

#### Testing User Isolation

```python
def test_users_cannot_access_others_data(client, db_session):
    """Test that users can only access their own medications."""
    # Create two users
    user1 = User(username="user1", email="user1@example.com", ...)
    user2 = User(username="user2", email="user2@example.com", ...)
    db_session.add_all([user1, user2])
    db_session.commit()

    # Create medication for user1
    med = Medication(user_id=user1.id, drug_name="User1 Med", ...)
    db_session.add(med)
    db_session.commit()

    # Login as user2
    response = client.post("/api/auth/login", ...)
    user2_token = response.json()["access_token"]
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    # Try to access user1's medication
    response = client.get(f"/api/medications/{med.id}", headers=user2_headers)
    assert response.status_code == 404
```

#### Testing Filtering and Pagination

```python
def test_filter_medications_by_tag(client, auth_headers, db_session, test_user):
    """Test filtering medications by tag."""
    # Setup: Create tag and medications
    tag = Tag(user_id=test_user.id, name="Morning")
    med1 = Medication(user_id=test_user.id, drug_name="Med1", ...)
    med1.tags.append(tag)
    med2 = Medication(user_id=test_user.id, drug_name="Med2", ...)
    # med2 has no tags
    db_session.add_all([med1, med2])
    db_session.commit()

    # Filter by tag
    response = client.get(
        f"/api/medications/?tag_ids={tag.id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    medications = response.json()["medications"]
    med_names = [m["drug_name"] for m in medications]
    assert "Med1" in med_names
    assert "Med2" not in med_names
```

### Testing Validation

```python
def test_invalid_color_format(client, auth_headers):
    """Test that invalid color format is rejected."""
    response = client.post(
        "/api/tags/",
        headers=auth_headers,
        json={"name": "Test", "color": "red"}  # Invalid format
    )

    assert response.status_code == 422
    assert "hex color code" in str(response.json()).lower()
```

## Testing Best Practices

### DO ✅

1. **Test One Thing Per Test**
   ```python
   # Good
   def test_medication_creation(db_session, test_user):
       medication = Medication(...)
       db_session.add(medication)
       db_session.commit()
       assert medication.id is not None

   def test_medication_default_active(db_session, test_user):
       medication = Medication(...)
       db_session.add(medication)
       db_session.commit()
       assert medication.active is True
   ```

2. **Use Descriptive Test Names**
   ```python
   # Good
   def test_user_cannot_access_other_user_medications(...)

   # Bad
   def test_medication_1(...)
   ```

3. **Follow AAA Pattern**
   ```python
   def test_example():
       # Arrange - Set up test data
       medication = Medication(...)

       # Act - Perform the action
       db_session.add(medication)
       db_session.commit()

       # Assert - Verify the results
       assert medication.id is not None
   ```

4. **Use Fixtures for Common Setup**
   ```python
   @pytest.fixture
   def sample_medication(db_session, test_user):
       med = Medication(user_id=test_user.id, ...)
       db_session.add(med)
       db_session.commit()
       return med
   ```

5. **Test Both Success and Failure Cases**
   ```python
   def test_create_tag_success(client, auth_headers):
       response = client.post("/api/tags/", ...)
       assert response.status_code == 201

   def test_create_tag_duplicate_name(client, auth_headers):
       client.post("/api/tags/", json={"name": "Duplicate"}, ...)
       response = client.post("/api/tags/", json={"name": "Duplicate"}, ...)
       assert response.status_code == 400
   ```

6. **Keep Tests Independent**
   - Each test should be able to run in isolation
   - Don't rely on test execution order
   - Use fixtures for setup, transaction rollback for cleanup

7. **Test Edge Cases**
   ```python
   def test_empty_tag_name(client, auth_headers):
       response = client.post("/api/tags/", json={"name": "   "}, ...)
       assert response.status_code == 422

   def test_very_long_drug_name(client, auth_headers):
       response = client.post("/api/medications/", json={"drug_name": "A" * 300}, ...)
       assert response.status_code == 422
   ```

### DON'T ❌

1. **Don't Test Framework Internals**
   ```python
   # Bad - Testing FastAPI/SQLAlchemy itself
   def test_fastapi_works():
       assert isinstance(app, FastAPI)
   ```

2. **Don't Use Real External Services**
   ```python
   # Bad
   def test_send_email():
       send_email_via_smtp(...)  # Uses real SMTP server

   # Good - Use mocks
   def test_send_email(mocker):
       mock_smtp = mocker.patch('app.utils.email.smtp')
       send_email(...)
       assert mock_smtp.send.called
   ```

3. **Don't Hardcode Test Data**
   ```python
   # Bad
   def test_medication():
       med = Medication(user_id="123-456-789", ...)

   # Good - Use fixtures
   def test_medication(test_user):
       med = Medication(user_id=test_user.id, ...)
   ```

4. **Don't Write Overly Complex Tests**
   ```python
   # Bad - Too complex, testing too much
   def test_complete_medication_workflow():
       # 50 lines of setup
       # Multiple assertions
       # Hard to debug when it fails

   # Good - Split into multiple focused tests
   def test_create_medication():
       ...

   def test_add_tag_to_medication():
       ...

   def test_update_medication():
       ...
   ```

5. **Don't Skip Cleanup**
   - Always use fixtures with proper cleanup
   - Use transaction rollback for database tests
   - Don't leave test data in the database

6. **Don't Ignore Flaky Tests**
   - If a test fails intermittently, fix it
   - Don't use `pytest.mark.skip` as a permanent solution
   - Investigate root cause of flakiness

## Continuous Integration

### GitHub Actions Example

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_DB: medtrack
          POSTGRES_USER: medtrack_user
          POSTGRES_PASSWORD: test_password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt -r requirements-dev.txt

      - name: Run tests
        env:
          DATABASE_URL: postgresql://medtrack_user:test_password@localhost:5432/medtrack
          SECRET_KEY: test-secret-key
        run: |
          cd backend
          pytest --cov=app --cov-report=xml --cov-fail-under=85

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml
```

## Troubleshooting

### Common Issues

**Issue**: Tests fail with "relation does not exist"
**Solution**: Run database migrations
```bash
docker-compose exec backend alembic upgrade head
```

**Issue**: Tests fail with "transaction already deassociated"
**Solution**: This is a warning that can usually be ignored. It occurs when a test intentionally causes a database error.

**Issue**: Coverage report not generated
**Solution**: Ensure pytest-cov is installed
```bash
docker-compose exec backend pip install pytest-cov
```

**Issue**: Tests are slow
**Solution**:
- Run only changed tests during development
- Use faster test database (in-memory SQLite for unit tests)
- Run integration tests separately from unit tests

### Debug Mode

Run tests with Python debugger:

```bash
docker-compose exec backend pytest --pdb
```

Run tests with print statements visible:

```bash
docker-compose exec backend pytest -s
```

## Test Maintenance

### Updating Tests After Code Changes

1. **After adding a new model field**:
   - Update model tests to test the new field
   - Update API tests to include the field in requests/responses
   - Update schema tests if validation changed

2. **After adding a new endpoint**:
   - Add integration tests for all CRUD operations
   - Test authentication requirements
   - Test error cases (400, 404, etc.)
   - Test user isolation

3. **After changing validation**:
   - Update schema tests
   - Add tests for new validation rules
   - Test both valid and invalid inputs

### Refactoring Tests

When tests become repetitive, consider:

1. **Creating custom fixtures**:
   ```python
   @pytest.fixture
   def medication_with_tags(db_session, test_user):
       medication = Medication(...)
       tags = [Tag(...) for _ in range(3)]
       medication.tags.extend(tags)
       db_session.add(medication)
       db_session.commit()
       return medication
   ```

2. **Using parametrized tests**:
   ```python
   @pytest.mark.parametrize("prescription_type", ["long_term", "short_term", "otc"])
   def test_medication_types(client, auth_headers, prescription_type):
       response = client.post("/api/medications/",
           json={"prescription_type": prescription_type, ...})
       assert response.status_code == 201
   ```

3. **Creating test helpers**:
   ```python
   def create_test_medication(db_session, user, **kwargs):
       defaults = {
           "drug_name": "Test Med",
           "standard_dose": "10mg",
           "start_date": date.today()
       }
       defaults.update(kwargs)
       med = Medication(user_id=user.id, **defaults)
       db_session.add(med)
       db_session.commit()
       return med
   ```

## Summary

- **Run tests frequently** during development
- **Maintain high coverage** (target: 85%+)
- **Write clear, focused tests** that are easy to understand
- **Test both happy paths and error cases**
- **Keep tests independent and fast**
- **Use fixtures and helpers** to reduce duplication
- **Integrate tests into CI/CD** pipeline

For more information, see the [pytest documentation](https://docs.pytest.org/).
