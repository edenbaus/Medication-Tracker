import pytest
from fastapi.testclient import TestClient
from app.models import User
from app.utils.security import get_password_hash


class TestAdminEndpoints:
    """Integration tests for admin API endpoints."""

    @pytest.fixture
    def admin_user(self, db_session):
        """Create an admin user for testing."""
        admin = User(
            username="admin",
            email="admin@example.com",
            password_hash=get_password_hash("adminpass123"),
            is_admin=True
        )
        db_session.add(admin)
        db_session.commit()
        db_session.refresh(admin)
        return admin

    @pytest.fixture
    def admin_headers(self, client: TestClient, admin_user):
        """Get authentication headers for admin user."""
        response = client.post(
            "/api/auth/login",
            data={"username": "admin@example.com", "password": "adminpass123"}
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    @pytest.fixture
    def regular_user(self, db_session):
        """Create a regular (non-admin) user for testing."""
        user = User(
            username="regular",
            email="regular@example.com",
            password_hash=get_password_hash("userpass123"),
            is_admin=False
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    @pytest.fixture
    def regular_headers(self, client: TestClient, regular_user):
        """Get authentication headers for regular user."""
        response = client.post(
            "/api/auth/login",
            data={"username": "regular@example.com", "password": "userpass123"}
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_get_all_users_as_admin(self, client: TestClient, admin_headers, db_session, admin_user, regular_user):
        """Test getting all users as admin."""
        response = client.get("/api/admin/users", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert data["total"] >= 2  # At least admin and regular user

        usernames = [u["username"] for u in data["users"]]
        assert "admin" in usernames
        assert "regular" in usernames

    def test_get_all_users_filter_by_admin_status(self, client: TestClient, admin_headers, db_session, admin_user, regular_user):
        """Test filtering users by admin status."""
        # Filter for admin users only
        response = client.get("/api/admin/users?is_admin=true", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        for user in data["users"]:
            assert user["is_admin"] is True

        # Filter for non-admin users only
        response = client.get("/api/admin/users?is_admin=false", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        for user in data["users"]:
            assert user["is_admin"] is False

    def test_get_all_users_pagination(self, client: TestClient, admin_headers, db_session, admin_user):
        """Test pagination for user list."""
        # Create multiple users
        for i in range(5):
            user = User(
                username=f"user{i}",
                email=f"user{i}@example.com",
                password_hash=get_password_hash("password"),
                is_admin=False
            )
            db_session.add(user)
        db_session.commit()

        # Get first page with limit of 3
        response = client.get("/api/admin/users?skip=0&limit=3", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["users"]) == 3
        assert data["page"] == 1
        assert data["page_size"] == 3

    def test_get_all_users_requires_admin(self, client: TestClient, regular_headers):
        """Test that getting all users requires admin access."""
        response = client.get("/api/admin/users", headers=regular_headers)

        assert response.status_code == 403
        assert "admin access required" in response.json()["detail"].lower()

    def test_get_all_users_requires_auth(self, client: TestClient):
        """Test that getting all users requires authentication."""
        response = client.get("/api/admin/users")

        assert response.status_code == 401

    def test_get_user_by_id_as_admin(self, client: TestClient, admin_headers, regular_user):
        """Test getting a specific user by ID as admin."""
        response = client.get(f"/api/admin/users/{regular_user.id}", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(regular_user.id)
        assert data["username"] == "regular"
        assert data["email"] == "regular@example.com"
        assert "is_admin" in data

    def test_get_user_by_id_not_found(self, client: TestClient, admin_headers):
        """Test getting a non-existent user."""
        response = client.get(
            "/api/admin/users/00000000-0000-0000-0000-000000000000",
            headers=admin_headers
        )

        assert response.status_code == 404

    def test_get_user_by_id_requires_admin(self, client: TestClient, regular_headers, admin_user):
        """Test that getting user by ID requires admin access."""
        response = client.get(f"/api/admin/users/{admin_user.id}", headers=regular_headers)

        assert response.status_code == 403

    def test_update_user_username(self, client: TestClient, admin_headers, regular_user, db_session):
        """Test updating a user's username."""
        response = client.put(
            f"/api/admin/users/{regular_user.id}",
            headers=admin_headers,
            json={"username": "newusername"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newusername"

        # Verify in database
        db_session.refresh(regular_user)
        assert regular_user.username == "newusername"

    def test_update_user_email(self, client: TestClient, admin_headers, regular_user, db_session):
        """Test updating a user's email."""
        response = client.put(
            f"/api/admin/users/{regular_user.id}",
            headers=admin_headers,
            json={"email": "newemail@example.com"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newemail@example.com"

        # Verify in database
        db_session.refresh(regular_user)
        assert regular_user.email == "newemail@example.com"

    def test_update_user_to_admin(self, client: TestClient, admin_headers, regular_user, db_session):
        """Test promoting a user to admin."""
        response = client.put(
            f"/api/admin/users/{regular_user.id}",
            headers=admin_headers,
            json={"is_admin": True}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_admin"] is True

        # Verify in database
        db_session.refresh(regular_user)
        assert regular_user.is_admin is True

    def test_update_user_demote_admin(self, client: TestClient, admin_headers, db_session):
        """Test demoting an admin to regular user."""
        # Create another admin
        admin2 = User(
            username="admin2",
            email="admin2@example.com",
            password_hash=get_password_hash("password"),
            is_admin=True
        )
        db_session.add(admin2)
        db_session.commit()

        response = client.put(
            f"/api/admin/users/{admin2.id}",
            headers=admin_headers,
            json={"is_admin": False}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_admin"] is False

    def test_update_user_duplicate_username(self, client: TestClient, admin_headers, regular_user, admin_user):
        """Test that updating to duplicate username is not allowed."""
        response = client.put(
            f"/api/admin/users/{regular_user.id}",
            headers=admin_headers,
            json={"username": "admin"}  # Admin's username
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_update_user_duplicate_email(self, client: TestClient, admin_headers, regular_user, admin_user):
        """Test that updating to duplicate email is not allowed."""
        response = client.put(
            f"/api/admin/users/{regular_user.id}",
            headers=admin_headers,
            json={"email": "admin@example.com"}  # Admin's email
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_update_user_not_found(self, client: TestClient, admin_headers):
        """Test updating a non-existent user."""
        response = client.put(
            "/api/admin/users/00000000-0000-0000-0000-000000000000",
            headers=admin_headers,
            json={"username": "test"}
        )

        assert response.status_code == 404

    def test_update_user_requires_admin(self, client: TestClient, regular_headers, admin_user):
        """Test that updating users requires admin access."""
        response = client.put(
            f"/api/admin/users/{admin_user.id}",
            headers=regular_headers,
            json={"username": "newestname"}
        )

        assert response.status_code == 403

    def test_delete_user_as_admin(self, client: TestClient, admin_headers, regular_user, db_session):
        """Test deleting a user as admin."""
        user_id = regular_user.id

        response = client.delete(f"/api/admin/users/{user_id}", headers=admin_headers)

        assert response.status_code == 204

        # Verify user is deleted
        user = db_session.query(User).filter_by(id=user_id).first()
        assert user is None

    def test_delete_user_cascade_deletes_data(self, client: TestClient, admin_headers, db_session):
        """Test that deleting a user CASCADE deletes their medications and tags."""
        from app.models import Medication, Tag
        from datetime import date

        # Create user with medications and tags
        user = User(
            username="user_to_delete",
            email="delete@example.com",
            password_hash=get_password_hash("password"),
            is_admin=False
        )
        db_session.add(user)
        db_session.commit()

        # Create medication and tag for this user
        tag = Tag(user_id=user.id, name="Test Tag")
        medication = Medication(
            user_id=user.id,
            drug_name="Test Med",
            standard_dose="10mg",
            start_date=date.today()
        )
        medication.tags.append(tag)
        db_session.add_all([tag, medication])
        db_session.commit()

        tag_id = tag.id
        med_id = medication.id
        user_id = user.id

        # Delete user
        response = client.delete(f"/api/admin/users/{user_id}", headers=admin_headers)
        assert response.status_code == 204

        # Verify cascade delete
        assert db_session.query(User).filter_by(id=user_id).first() is None
        assert db_session.query(Tag).filter_by(id=tag_id).first() is None
        assert db_session.query(Medication).filter_by(id=med_id).first() is None

    def test_delete_user_cannot_delete_self(self, client: TestClient, admin_headers, admin_user):
        """Test that admin cannot delete their own account."""
        response = client.delete(f"/api/admin/users/{admin_user.id}", headers=admin_headers)

        assert response.status_code == 400
        assert "cannot delete your own account" in response.json()["detail"].lower()

    def test_delete_user_not_found(self, client: TestClient, admin_headers):
        """Test deleting a non-existent user."""
        response = client.delete(
            "/api/admin/users/00000000-0000-0000-0000-000000000000",
            headers=admin_headers
        )

        assert response.status_code == 404

    def test_delete_user_requires_admin(self, client: TestClient, regular_headers, admin_user):
        """Test that deleting users requires admin access."""
        response = client.delete(f"/api/admin/users/{admin_user.id}", headers=regular_headers)

        assert response.status_code == 403

    def test_admin_user_response_includes_admin_field(self, client: TestClient, admin_headers, admin_user):
        """Test that admin endpoints return is_admin field in responses."""
        response = client.get(f"/api/admin/users/{admin_user.id}", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert "is_admin" in data
        assert data["is_admin"] is True
