import pytest
from datetime import date
from fastapi.testclient import TestClient
from app.models import Tag, Medication


class TestTagEndpoints:
    """Integration tests for tag API endpoints."""

    def test_create_tag_basic(self, client: TestClient, auth_headers):
        """Test creating a basic tag."""
        response = client.post(
            "/api/tags/",
            headers=auth_headers,
            json={"name": "Morning"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Morning"
        assert data["color"] is None
        assert "id" in data
        assert "user_id" in data

    def test_create_tag_with_color(self, client: TestClient, auth_headers):
        """Test creating a tag with a color."""
        response = client.post(
            "/api/tags/",
            headers=auth_headers,
            json={"name": "Heart Health", "color": "#FF5733"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Heart Health"
        assert data["color"] == "#FF5733"

    def test_create_tag_invalid_color(self, client: TestClient, auth_headers):
        """Test creating a tag with an invalid color format."""
        response = client.post(
            "/api/tags/",
            headers=auth_headers,
            json={"name": "Test", "color": "red"}
        )

        assert response.status_code == 422
        assert "hex color code" in str(response.json()).lower()

    def test_create_tag_duplicate_name(self, client: TestClient, auth_headers, db_session, test_user):
        """Test that duplicate tag names are not allowed for the same user."""
        # Create first tag
        tag = Tag(user_id=test_user.id, name="Duplicate")
        db_session.add(tag)
        db_session.commit()

        # Try to create duplicate
        response = client.post(
            "/api/tags/",
            headers=auth_headers,
            json={"name": "Duplicate"}
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_create_tag_empty_name(self, client: TestClient, auth_headers):
        """Test that empty tag names are not allowed."""
        response = client.post(
            "/api/tags/",
            headers=auth_headers,
            json={"name": "   "}
        )

        assert response.status_code == 422

    def test_create_tag_requires_auth(self, client: TestClient):
        """Test that creating a tag requires authentication."""
        response = client.post(
            "/api/tags/",
            json={"name": "Test"}
        )

        assert response.status_code == 401

    def test_get_tags_list(self, client: TestClient, auth_headers, db_session, test_user):
        """Test getting list of tags."""
        # Create some tags
        tag1 = Tag(user_id=test_user.id, name="Tag1", color="#FF0000")
        tag2 = Tag(user_id=test_user.id, name="Tag2", color="#00FF00")
        db_session.add_all([tag1, tag2])
        db_session.commit()

        response = client.get("/api/tags/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2
        assert len(data["tags"]) >= 2
        tag_names = [tag["name"] for tag in data["tags"]]
        assert "Tag1" in tag_names
        assert "Tag2" in tag_names

    def test_get_tags_with_counts(self, client: TestClient, auth_headers, db_session, test_user):
        """Test getting tags with medication counts."""
        # Create tags
        tag1 = Tag(user_id=test_user.id, name="Tag1")
        tag2 = Tag(user_id=test_user.id, name="Tag2")
        db_session.add_all([tag1, tag2])
        db_session.commit()

        # Create medications with tags
        med1 = Medication(
            user_id=test_user.id,
            drug_name="Med1",
            standard_dose="10mg",
            start_date=date.today(),
            active=True
        )
        med1.tags.append(tag1)

        med2 = Medication(
            user_id=test_user.id,
            drug_name="Med2",
            standard_dose="20mg",
            start_date=date.today(),
            active=True
        )
        med2.tags.append(tag1)

        med3 = Medication(
            user_id=test_user.id,
            drug_name="Med3",
            standard_dose="30mg",
            start_date=date.today(),
            active=False  # Inactive medication
        )
        med3.tags.append(tag1)

        db_session.add_all([med1, med2, med3])
        db_session.commit()

        response = client.get("/api/tags/with-counts", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Find tag1 in response
        tag1_data = next((t for t in data if t["name"] == "Tag1"), None)
        assert tag1_data is not None
        assert tag1_data["medication_count"] == 2  # Only active medications counted

        # Find tag2 in response
        tag2_data = next((t for t in data if t["name"] == "Tag2"), None)
        assert tag2_data is not None
        assert tag2_data["medication_count"] == 0

    def test_get_tag_by_id(self, client: TestClient, auth_headers, db_session, test_user):
        """Test getting a specific tag by ID."""
        tag = Tag(user_id=test_user.id, name="Specific Tag", color="#123456")
        db_session.add(tag)
        db_session.commit()

        response = client.get(f"/api/tags/{tag.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(tag.id)
        assert data["name"] == "Specific Tag"
        assert data["color"] == "#123456"

    def test_get_tag_not_found(self, client: TestClient, auth_headers):
        """Test getting a non-existent tag."""
        response = client.get(
            "/api/tags/00000000-0000-0000-0000-000000000000",
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_get_tag_different_user(self, client: TestClient, db_session):
        """Test that users cannot access other users' tags."""
        from app.models import User
        from app.utils.security import get_password_hash

        # Create two users
        user1 = User(
            username="user1",
            email="user1@example.com",
            password_hash=get_password_hash("password")
        )
        user2 = User(
            username="user2",
            email="user2@example.com",
            password_hash=get_password_hash("password")
        )
        db_session.add_all([user1, user2])
        db_session.commit()

        # Create tag for user1
        tag = Tag(user_id=user1.id, name="User1 Tag")
        db_session.add(tag)
        db_session.commit()

        # Login as user2
        login_response = client.post(
            "/api/auth/login",
            data={"username": "user2@example.com", "password": "password"}
        )
        user2_token = login_response.json()["access_token"]
        user2_headers = {"Authorization": f"Bearer {user2_token}"}

        # Try to access user1's tag
        response = client.get(f"/api/tags/{tag.id}", headers=user2_headers)

        assert response.status_code == 404

    def test_update_tag_name(self, client: TestClient, auth_headers, db_session, test_user):
        """Test updating a tag's name."""
        tag = Tag(user_id=test_user.id, name="Original Name")
        db_session.add(tag)
        db_session.commit()

        response = client.put(
            f"/api/tags/{tag.id}",
            headers=auth_headers,
            json={"name": "Updated Name"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"

    def test_update_tag_color(self, client: TestClient, auth_headers, db_session, test_user):
        """Test updating a tag's color."""
        tag = Tag(user_id=test_user.id, name="Test Tag", color="#FF0000")
        db_session.add(tag)
        db_session.commit()

        response = client.put(
            f"/api/tags/{tag.id}",
            headers=auth_headers,
            json={"color": "#00FF00"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Tag"  # Unchanged
        assert data["color"] == "#00FF00"  # Updated

    def test_update_tag_duplicate_name(self, client: TestClient, auth_headers, db_session, test_user):
        """Test that updating to a duplicate name is not allowed."""
        tag1 = Tag(user_id=test_user.id, name="Existing Tag")
        tag2 = Tag(user_id=test_user.id, name="Tag to Update")
        db_session.add_all([tag1, tag2])
        db_session.commit()

        response = client.put(
            f"/api/tags/{tag2.id}",
            headers=auth_headers,
            json={"name": "Existing Tag"}
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_update_tag_invalid_color(self, client: TestClient, auth_headers, db_session, test_user):
        """Test updating a tag with an invalid color."""
        tag = Tag(user_id=test_user.id, name="Test Tag")
        db_session.add(tag)
        db_session.commit()

        response = client.put(
            f"/api/tags/{tag.id}",
            headers=auth_headers,
            json={"color": "invalid"}
        )

        assert response.status_code == 422

    def test_delete_tag(self, client: TestClient, auth_headers, db_session, test_user):
        """Test deleting a tag."""
        tag = Tag(user_id=test_user.id, name="To Delete")
        db_session.add(tag)
        db_session.commit()
        tag_id = tag.id

        response = client.delete(f"/api/tags/{tag_id}", headers=auth_headers)

        assert response.status_code == 204

        # Verify tag is deleted
        tag = db_session.query(Tag).filter_by(id=tag_id).first()
        assert tag is None

    def test_delete_tag_removes_from_medications(self, client: TestClient, auth_headers, db_session, test_user):
        """Test that deleting a tag removes it from all medications."""
        tag = Tag(user_id=test_user.id, name="To Delete")
        medication = Medication(
            user_id=test_user.id,
            drug_name="Test Med",
            standard_dose="10mg",
            start_date=date.today()
        )
        medication.tags.append(tag)
        db_session.add(medication)
        db_session.commit()

        tag_id = tag.id
        med_id = medication.id

        # Delete tag
        response = client.delete(f"/api/tags/{tag_id}", headers=auth_headers)
        assert response.status_code == 204

        # Verify tag is removed from medication
        db_session.expire(medication)
        medication = db_session.query(Medication).filter_by(id=med_id).first()
        assert len(medication.tags) == 0

    def test_get_tag_medications(self, client: TestClient, auth_headers, db_session, test_user):
        """Test getting medications for a specific tag."""
        tag = Tag(user_id=test_user.id, name="Test Tag")

        # Create medications with and without the tag
        med1 = Medication(
            user_id=test_user.id,
            drug_name="Med1",
            standard_dose="10mg",
            start_date=date.today(),
            active=True
        )
        med1.tags.append(tag)

        med2 = Medication(
            user_id=test_user.id,
            drug_name="Med2",
            standard_dose="20mg",
            start_date=date.today(),
            active=True
        )
        med2.tags.append(tag)

        med3 = Medication(
            user_id=test_user.id,
            drug_name="Med3",
            standard_dose="30mg",
            start_date=date.today(),
            active=True
        )
        # med3 does not have the tag

        med4 = Medication(
            user_id=test_user.id,
            drug_name="Med4",
            standard_dose="40mg",
            start_date=date.today(),
            active=False  # Inactive
        )
        med4.tags.append(tag)

        db_session.add_all([med1, med2, med3, med4])
        db_session.commit()

        response = client.get(f"/api/tags/{tag.id}/medications", headers=auth_headers)

        assert response.status_code == 200
        medication_ids = response.json()
        assert len(medication_ids) == 2  # Only active medications
        assert str(med1.id) in medication_ids
        assert str(med2.id) in medication_ids
        assert str(med3.id) not in medication_ids
        assert str(med4.id) not in medication_ids  # Inactive

    def test_different_users_same_tag_names(self, client: TestClient, db_session):
        """Test that different users can have tags with the same name."""
        from app.models import User
        from app.utils.security import get_password_hash

        # Create two users
        user1 = User(
            username="user1",
            email="user1@example.com",
            password_hash=get_password_hash("password")
        )
        user2 = User(
            username="user2",
            email="user2@example.com",
            password_hash=get_password_hash("password")
        )
        db_session.add_all([user1, user2])
        db_session.commit()

        # Login as user1 and create tag
        login_response = client.post(
            "/api/auth/login",
            data={"username": "user1@example.com", "password": "password"}
        )
        user1_token = login_response.json()["access_token"]
        user1_headers = {"Authorization": f"Bearer {user1_token}"}

        response1 = client.post(
            "/api/tags/",
            headers=user1_headers,
            json={"name": "Morning"}
        )
        assert response1.status_code == 201

        # Login as user2 and create tag with same name
        login_response = client.post(
            "/api/auth/login",
            data={"username": "user2@example.com", "password": "password"}
        )
        user2_token = login_response.json()["access_token"]
        user2_headers = {"Authorization": f"Bearer {user2_token}"}

        response2 = client.post(
            "/api/tags/",
            headers=user2_headers,
            json={"name": "Morning"}
        )
        assert response2.status_code == 201

        # Verify both tags exist and are different
        assert response1.json()["id"] != response2.json()["id"]
