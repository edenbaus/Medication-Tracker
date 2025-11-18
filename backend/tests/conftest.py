import pytest
import os
from datetime import date, datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.utils.security import get_password_hash
from tests.factories.factories import (
    UserFactory,
    ThirdPartyFactory,
    TagFactory,
    MedicationFactory,
    MedicationLogFactory,
    SideEffectFactory,
    SymptomFactory,
    RegimenFactory,
)


# Use the actual PostgreSQL database from docker-compose for testing
# This is more realistic and supports all PostgreSQL features like UUID, JSONB, ENUMs
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://medtrack_user:medtrack_dev_pass_2024@postgres:5432/medtrack"
)

engine = create_engine(DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database session for each test.

    Uses transaction rollback to clean up data after each test.

    Yields:
        Session: Database session for testing
    """
    connection = engine.connect()
    transaction = connection.begin()
    db = TestingSessionLocal(bind=connection)

    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a test client with dependency override.

    Args:
        db_session: Test database session

    Yields:
        TestClient: FastAPI test client
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """
    Create a test user.

    Args:
        db_session: Database session

    Returns:
        User: Test user object
    """
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=get_password_hash("testpassword123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, test_user):
    """
    Get authentication headers for test user.

    Args:
        client: Test client
        test_user: Test user

    Returns:
        dict: Headers with authentication token
    """
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_user.email,  # OAuth2 uses 'username' field
            "password": "testpassword123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_user(db_session):
    """Create an admin user for testing."""
    return UserFactory.create(
        db_session,
        username="adminuser",
        email="admin@example.com",
        password="adminpassword123",
        is_admin=True
    )


@pytest.fixture
def admin_headers(client, admin_user):
    """Get authentication headers for admin user."""
    response = client.post(
        "/api/auth/login",
        data={
            "username": admin_user.email,
            "password": "adminpassword123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_third_party(db_session, test_user):
    """Create a test third party."""
    return ThirdPartyFactory.create(
        db_session,
        test_user,
        name="Child",
        relationship_type="child"
    )


@pytest.fixture
def test_tag(db_session, test_user):
    """Create a test tag."""
    return TagFactory.create(
        db_session,
        test_user,
        name="Important",
        color="#FF0000"
    )


@pytest.fixture
def test_medication(db_session, test_user):
    """Create a test medication."""
    return MedicationFactory.create(
        db_session,
        test_user,
        drug_name="Aspirin",
        standard_dose="100mg",
        date_filled=date.today() - timedelta(days=15),
        days_supply=30,
        refills_total=5,
        refills_used=0
    )


@pytest.fixture
def test_medication_log(db_session, test_medication):
    """Create a test medication log."""
    return MedicationLogFactory.create(
        db_session,
        test_medication,
        dose_taken="100mg",
        taken_at=datetime.utcnow()
    )


@pytest.fixture
def test_side_effect(db_session, test_user, test_medication):
    """Create a test side effect."""
    return SideEffectFactory.create(
        db_session,
        test_user,
        test_medication,
        description="Headache",
        severity="mild"
    )


@pytest.fixture
def test_symptom(db_session, test_user, test_medication):
    """Create a test symptom."""
    return SymptomFactory.create(
        db_session,
        test_user,
        test_medication,
        symptom_name="Pain",
        improvement_level=7
    )


@pytest.fixture
def test_regimen(db_session, test_user):
    """Create a test regimen."""
    return RegimenFactory.create(
        db_session,
        test_user,
        name="Morning Regimen",
        description="Morning medication schedule"
    )
