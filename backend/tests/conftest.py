import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.utils.security import get_password_hash


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
