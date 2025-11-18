import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from app.models import Medication, Tag, PrescriptionType


class TestMedicationEndpoints:
    """Integration tests for medication API endpoints."""

    def test_create_medication_basic(self, client: TestClient, auth_headers):
        """Test creating a basic medication."""
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
        assert data["standard_dose"] == "100mg"
        assert data["prescription_type"] == "otc"
        assert data["active"] is True
        assert "id" in data
        assert "user_id" in data

    def test_create_medication_with_all_fields(self, client: TestClient, auth_headers):
        """Test creating a medication with all fields populated."""
        start = date.today()
        end = start + timedelta(days=10)

        response = client.post(
            "/api/medications/",
            headers=auth_headers,
            json={
                "drug_name": "Amoxicillin",
                "pharmacy": "CVS Pharmacy",
                "prescription_type": "short_term",
                "dosing_schedule": {
                    "frequency": "3 times daily",
                    "times": ["08:00", "14:00", "20:00"],
                    "with_food": True
                },
                "standard_dose": "500mg",
                "date_prescribed": str(start),
                "date_filled": str(start),
                "prescribing_doctor": "Dr. Smith",
                "prescription_number": "RX123456",
                "notes": "Take with food to avoid stomach upset",
                "start_date": str(start),
                "end_date": str(end)
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["drug_name"] == "Amoxicillin"
        assert data["pharmacy"] == "CVS Pharmacy"
        assert data["dosing_schedule"]["frequency"] == "3 times daily"
        assert len(data["dosing_schedule"]["times"]) == 3
        assert data["prescribing_doctor"] == "Dr. Smith"
        assert data["notes"] == "Take with food to avoid stomach upset"

    def test_create_medication_with_tags(self, client: TestClient, auth_headers):
        """Test creating a medication with tags."""
        # Create tags first
        tag1_response = client.post(
            "/api/tags/",
            headers=auth_headers,
            json={"name": "Morning", "color": "#FF5733"}
        )
        tag2_response = client.post(
            "/api/tags/",
            headers=auth_headers,
            json={"name": "Heart Health", "color": "#33C3FF"}
        )

        tag1_id = tag1_response.json()["id"]
        tag2_id = tag2_response.json()["id"]

        # Create medication with tags
        response = client.post(
            "/api/medications/",
            headers=auth_headers,
            json={
                "drug_name": "Atorvastatin",
                "standard_dose": "20mg",
                "prescription_type": "long_term",
                "start_date": str(date.today()),
                "tag_ids": [tag1_id, tag2_id]
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert len(data["tags"]) == 2
        tag_names = [tag["name"] for tag in data["tags"]]
        assert "Morning" in tag_names
        assert "Heart Health" in tag_names

    def test_create_medication_with_invalid_tag(self, client: TestClient, auth_headers):
        """Test creating a medication with non-existent tag ID."""
        response = client.post(
            "/api/medications/",
            headers=auth_headers,
            json={
                "drug_name": "Test Med",
                "standard_dose": "10mg",
                "prescription_type": "otc",
                "start_date": str(date.today()),
                "tag_ids": ["00000000-0000-0000-0000-000000000000"]
            }
        )

        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()

    def test_create_medication_requires_auth(self, client: TestClient):
        """Test that creating a medication requires authentication."""
        response = client.post(
            "/api/medications/",
            json={
                "drug_name": "Test",
                "standard_dose": "10mg",
                "prescription_type": "otc",
                "start_date": str(date.today())
            }
        )

        assert response.status_code == 401

    def test_get_medications_list(self, client: TestClient, auth_headers, db_session, test_user):
        """Test getting list of medications."""
        # Create some medications
        med1 = Medication(
            user_id=test_user.id,
            drug_name="Med1",
            standard_dose="10mg",
            start_date=date.today()
        )
        med2 = Medication(
            user_id=test_user.id,
            drug_name="Med2",
            standard_dose="20mg",
            start_date=date.today()
        )
        db_session.add_all([med1, med2])
        db_session.commit()

        response = client.get("/api/medications/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2
        assert len(data["medications"]) >= 2

    def test_get_medications_filter_by_active(self, client: TestClient, auth_headers, db_session, test_user):
        """Test filtering medications by active status."""
        # Create active and inactive medications
        active_med = Medication(
            user_id=test_user.id,
            drug_name="Active Med",
            standard_dose="10mg",
            active=True,
            start_date=date.today()
        )
        inactive_med = Medication(
            user_id=test_user.id,
            drug_name="Inactive Med",
            standard_dose="20mg",
            active=False,
            start_date=date.today()
        )
        db_session.add_all([active_med, inactive_med])
        db_session.commit()

        # Filter for active only
        response = client.get("/api/medications/?active=true", headers=auth_headers)
        assert response.status_code == 200
        medications = response.json()["medications"]
        assert all(med["active"] is True for med in medications)

        # Filter for inactive only
        response = client.get("/api/medications/?active=false", headers=auth_headers)
        assert response.status_code == 200
        medications = response.json()["medications"]
        assert all(med["active"] is False for med in medications)

    def test_get_medications_filter_by_type(self, client: TestClient, auth_headers, db_session, test_user):
        """Test filtering medications by prescription type."""
        # Create medications of different types
        otc = Medication(
            user_id=test_user.id,
            drug_name="OTC Med",
            standard_dose="10mg",
            prescription_type=PrescriptionType.OTC,
            start_date=date.today()
        )
        long_term = Medication(
            user_id=test_user.id,
            drug_name="Long Term Med",
            standard_dose="20mg",
            prescription_type=PrescriptionType.LONG_TERM,
            start_date=date.today()
        )
        db_session.add_all([otc, long_term])
        db_session.commit()

        response = client.get("/api/medications/?prescription_type=otc", headers=auth_headers)
        assert response.status_code == 200
        medications = response.json()["medications"]
        assert all(med["prescription_type"] == "otc" for med in medications)

    def test_get_medications_filter_by_tags(self, client: TestClient, auth_headers, db_session, test_user):
        """Test filtering medications by tags."""
        # Create tags
        tag1 = Tag(user_id=test_user.id, name="Tag1")
        tag2 = Tag(user_id=test_user.id, name="Tag2")

        # Create medications with tags
        med1 = Medication(
            user_id=test_user.id,
            drug_name="Med1",
            standard_dose="10mg",
            start_date=date.today()
        )
        med1.tags.append(tag1)

        med2 = Medication(
            user_id=test_user.id,
            drug_name="Med2",
            standard_dose="20mg",
            start_date=date.today()
        )
        med2.tags.append(tag2)

        med3 = Medication(
            user_id=test_user.id,
            drug_name="Med3",
            standard_dose="30mg",
            start_date=date.today()
        )
        med3.tags.extend([tag1, tag2])

        db_session.add_all([med1, med2, med3])
        db_session.commit()

        # Filter by tag1
        response = client.get(f"/api/medications/?tag_ids={tag1.id}", headers=auth_headers)
        assert response.status_code == 200
        medications = response.json()["medications"]
        med_names = [med["drug_name"] for med in medications]
        assert "Med1" in med_names
        assert "Med3" in med_names
        assert "Med2" not in med_names

    def test_get_medications_pagination(self, client: TestClient, auth_headers, db_session, test_user):
        """Test pagination of medication list."""
        # Create multiple medications
        for i in range(15):
            med = Medication(
                user_id=test_user.id,
                drug_name=f"Med{i}",
                standard_dose="10mg",
                start_date=date.today()
            )
            db_session.add(med)
        db_session.commit()

        # Get first page
        response = client.get("/api/medications/?skip=0&limit=5", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["medications"]) == 5
        assert data["total"] >= 15
        assert data["page"] == 1
        assert data["page_size"] == 5

        # Get second page
        response = client.get("/api/medications/?skip=5&limit=5", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["medications"]) == 5
        assert data["page"] == 2

    def test_get_medication_by_id(self, client: TestClient, auth_headers, db_session, test_user):
        """Test getting a specific medication by ID."""
        medication = Medication(
            user_id=test_user.id,
            drug_name="Specific Med",
            standard_dose="10mg",
            start_date=date.today()
        )
        db_session.add(medication)
        db_session.commit()

        response = client.get(f"/api/medications/{medication.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(medication.id)
        assert data["drug_name"] == "Specific Med"

    def test_get_medication_not_found(self, client: TestClient, auth_headers):
        """Test getting a non-existent medication."""
        response = client.get(
            "/api/medications/00000000-0000-0000-0000-000000000000",
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_get_medication_different_user(self, client: TestClient, db_session):
        """Test that users cannot access other users' medications."""
        # Create another user
        from app.models import User
        from app.utils.security import get_password_hash

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

        # Create medication for user1
        medication = Medication(
            user_id=user1.id,
            drug_name="User1 Med",
            standard_dose="10mg",
            start_date=date.today()
        )
        db_session.add(medication)
        db_session.commit()

        # Login as user2
        login_response = client.post(
            "/api/auth/login",
            data={"username": "user2@example.com", "password": "password"}
        )
        user2_token = login_response.json()["access_token"]
        user2_headers = {"Authorization": f"Bearer {user2_token}"}

        # Try to access user1's medication
        response = client.get(
            f"/api/medications/{medication.id}",
            headers=user2_headers
        )

        assert response.status_code == 404

    def test_update_medication(self, client: TestClient, auth_headers, db_session, test_user):
        """Test updating a medication."""
        medication = Medication(
            user_id=test_user.id,
            drug_name="Original Name",
            standard_dose="10mg",
            start_date=date.today()
        )
        db_session.add(medication)
        db_session.commit()

        response = client.put(
            f"/api/medications/{medication.id}",
            headers=auth_headers,
            json={
                "drug_name": "Updated Name",
                "standard_dose": "20mg",
                "notes": "New notes"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["drug_name"] == "Updated Name"
        assert data["standard_dose"] == "20mg"
        assert data["notes"] == "New notes"

    def test_update_medication_partial(self, client: TestClient, auth_headers, db_session, test_user):
        """Test partial update of a medication."""
        medication = Medication(
            user_id=test_user.id,
            drug_name="Original Name",
            standard_dose="10mg",
            pharmacy="CVS",
            start_date=date.today()
        )
        db_session.add(medication)
        db_session.commit()

        response = client.put(
            f"/api/medications/{medication.id}",
            headers=auth_headers,
            json={"pharmacy": "Walgreens"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["drug_name"] == "Original Name"  # Unchanged
        assert data["pharmacy"] == "Walgreens"  # Updated

    def test_delete_medication(self, client: TestClient, auth_headers, db_session, test_user):
        """Test soft deleting a medication."""
        medication = Medication(
            user_id=test_user.id,
            drug_name="To Delete",
            standard_dose="10mg",
            active=True,
            start_date=date.today()
        )
        db_session.add(medication)
        db_session.commit()
        med_id = medication.id

        response = client.delete(f"/api/medications/{med_id}", headers=auth_headers)

        assert response.status_code == 204

        # Verify medication is soft deleted
        db_session.expire(medication)
        medication = db_session.query(Medication).filter_by(id=med_id).first()
        assert medication.active is False

    def test_add_tag_to_medication(self, client: TestClient, auth_headers, db_session, test_user):
        """Test adding a tag to a medication."""
        medication = Medication(
            user_id=test_user.id,
            drug_name="Test Med",
            standard_dose="10mg",
            start_date=date.today()
        )
        tag = Tag(user_id=test_user.id, name="Test Tag")
        db_session.add_all([medication, tag])
        db_session.commit()

        response = client.post(
            f"/api/medications/{medication.id}/tags/{tag.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["tags"]) == 1
        assert data["tags"][0]["name"] == "Test Tag"

    def test_add_duplicate_tag_to_medication(self, client: TestClient, auth_headers, db_session, test_user):
        """Test adding the same tag twice to a medication."""
        medication = Medication(
            user_id=test_user.id,
            drug_name="Test Med",
            standard_dose="10mg",
            start_date=date.today()
        )
        tag = Tag(user_id=test_user.id, name="Test Tag")
        medication.tags.append(tag)
        db_session.add(medication)
        db_session.commit()

        response = client.post(
            f"/api/medications/{medication.id}/tags/{tag.id}",
            headers=auth_headers
        )

        assert response.status_code == 400
        assert "already assigned" in response.json()["detail"].lower()

    def test_remove_tag_from_medication(self, client: TestClient, auth_headers, db_session, test_user):
        """Test removing a tag from a medication."""
        medication = Medication(
            user_id=test_user.id,
            drug_name="Test Med",
            standard_dose="10mg",
            start_date=date.today()
        )
        tag = Tag(user_id=test_user.id, name="Test Tag")
        medication.tags.append(tag)
        db_session.add(medication)
        db_session.commit()

        response = client.delete(
            f"/api/medications/{medication.id}/tags/{tag.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["tags"]) == 0

    def test_remove_unassigned_tag_from_medication(self, client: TestClient, auth_headers, db_session, test_user):
        """Test removing a tag that is not assigned to the medication."""
        medication = Medication(
            user_id=test_user.id,
            drug_name="Test Med",
            standard_dose="10mg",
            start_date=date.today()
        )
        tag = Tag(user_id=test_user.id, name="Test Tag")
        db_session.add_all([medication, tag])
        db_session.commit()

        response = client.delete(
            f"/api/medications/{medication.id}/tags/{tag.id}",
            headers=auth_headers
        )

        assert response.status_code == 400
        assert "not assigned" in response.json()["detail"].lower()
