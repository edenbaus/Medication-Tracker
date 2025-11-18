import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.models import Medication, MedicationLog, Tag
from datetime import date


class TestMedicationLogEndpoints:
    """Integration tests for medication log API endpoints."""

    @pytest.fixture
    def sample_medication(self, db_session, test_user):
        """Create a sample medication for testing."""
        medication = Medication(
            user_id=test_user.id,
            drug_name="Test Medication",
            standard_dose="10mg",
            start_date=date.today(),
            active=True
        )
        db_session.add(medication)
        db_session.commit()
        db_session.refresh(medication)
        return medication

    def test_create_medication_log(self, client: TestClient, auth_headers, sample_medication):
        """Test creating a medication log entry."""
        response = client.post(
            "/api/logs/",
            headers=auth_headers,
            json={
                "medication_id": str(sample_medication.id),
                "dose_taken": "10mg"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["medication_id"] == str(sample_medication.id)
        assert data["dose_taken"] == "10mg"
        assert "id" in data
        assert "taken_at" in data

    def test_create_log_with_custom_time(self, client: TestClient, auth_headers, sample_medication):
        """Test creating a log entry with custom timestamp."""
        custom_time = (datetime.utcnow() - timedelta(hours=2)).isoformat()

        response = client.post(
            "/api/logs/",
            headers=auth_headers,
            json={
                "medication_id": str(sample_medication.id),
                "dose_taken": "20mg",
                "taken_at": custom_time
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["dose_taken"] == "20mg"

    def test_create_log_with_notes(self, client: TestClient, auth_headers, sample_medication):
        """Test creating a log entry with notes."""
        response = client.post(
            "/api/logs/",
            headers=auth_headers,
            json={
                "medication_id": str(sample_medication.id),
                "dose_taken": "10mg",
                "notes": "Took with food"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["notes"] == "Took with food"

    def test_create_log_future_time_fails(self, client: TestClient, auth_headers, sample_medication):
        """Test that creating a log with future timestamp fails."""
        future_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()

        response = client.post(
            "/api/logs/",
            headers=auth_headers,
            json={
                "medication_id": str(sample_medication.id),
                "dose_taken": "10mg",
                "taken_at": future_time
            }
        )

        assert response.status_code == 422

    def test_create_log_empty_dose_fails(self, client: TestClient, auth_headers, sample_medication):
        """Test that creating a log with empty dose fails."""
        response = client.post(
            "/api/logs/",
            headers=auth_headers,
            json={
                "medication_id": str(sample_medication.id),
                "dose_taken": "   "
            }
        )

        assert response.status_code == 422

    def test_create_log_nonexistent_medication(self, client: TestClient, auth_headers):
        """Test creating a log for non-existent medication."""
        response = client.post(
            "/api/logs/",
            headers=auth_headers,
            json={
                "medication_id": "00000000-0000-0000-0000-000000000000",
                "dose_taken": "10mg"
            }
        )

        assert response.status_code == 404

    def test_create_log_requires_auth(self, client: TestClient, sample_medication):
        """Test that creating a log requires authentication."""
        response = client.post(
            "/api/logs/",
            json={
                "medication_id": str(sample_medication.id),
                "dose_taken": "10mg"
            }
        )

        assert response.status_code == 401

    def test_get_medication_logs(self, client: TestClient, auth_headers, db_session, sample_medication, test_user):
        """Test getting list of medication logs."""
        # Create some logs
        log1 = MedicationLog(
            medication_id=sample_medication.id,
            user_id=test_user.id,
            dose_taken="10mg",
            taken_at=datetime.utcnow() - timedelta(hours=2)
        )
        log2 = MedicationLog(
            medication_id=sample_medication.id,
            user_id=test_user.id,
            dose_taken="10mg",
            taken_at=datetime.utcnow() - timedelta(hours=1)
        )
        db_session.add_all([log1, log2])
        db_session.commit()

        response = client.get("/api/logs/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2
        assert len(data["logs"]) >= 2

    def test_get_logs_filter_by_medication(self, client: TestClient, auth_headers, db_session, test_user):
        """Test filtering logs by medication."""
        # Create two medications
        med1 = Medication(user_id=test_user.id, drug_name="Med1", standard_dose="10mg", start_date=date.today())
        med2 = Medication(user_id=test_user.id, drug_name="Med2", standard_dose="20mg", start_date=date.today())
        db_session.add_all([med1, med2])
        db_session.commit()

        # Create logs for each
        log1 = MedicationLog(medication_id=med1.id, user_id=test_user.id, dose_taken="10mg", taken_at=datetime.utcnow())
        log2 = MedicationLog(medication_id=med2.id, user_id=test_user.id, dose_taken="20mg", taken_at=datetime.utcnow())
        db_session.add_all([log1, log2])
        db_session.commit()

        # Filter by med1
        response = client.get(f"/api/logs/?medication_id={med1.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert all(log["medication_id"] == str(med1.id) for log in data["logs"])

    def test_get_logs_filter_by_date_range(self, client: TestClient, auth_headers, db_session, sample_medication, test_user):
        """Test filtering logs by date range."""
        # Create logs at different times
        old_log = MedicationLog(
            medication_id=sample_medication.id,
            user_id=test_user.id,
            dose_taken="10mg",
            taken_at=datetime.utcnow() - timedelta(days=10)
        )
        recent_log = MedicationLog(
            medication_id=sample_medication.id,
            user_id=test_user.id,
            dose_taken="10mg",
            taken_at=datetime.utcnow()
        )
        db_session.add_all([old_log, recent_log])
        db_session.commit()

        # Filter for last 5 days
        start_date = (datetime.utcnow() - timedelta(days=5)).isoformat()
        response = client.get(f"/api/logs/?start_date={start_date}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        # Should only get recent log
        assert all(
            datetime.fromisoformat(log["taken_at"]) >= datetime.fromisoformat(start_date)
            for log in data["logs"]
        )

    def test_get_logs_pagination(self, client: TestClient, auth_headers, db_session, sample_medication, test_user):
        """Test pagination of logs."""
        # Create multiple logs
        for i in range(10):
            log = MedicationLog(
                medication_id=sample_medication.id,
                user_id=test_user.id,
                dose_taken=f"{i}mg",
                taken_at=datetime.utcnow() - timedelta(hours=i)
            )
            db_session.add(log)
        db_session.commit()

        # Get first page
        response = client.get("/api/logs/?skip=0&limit=5", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["logs"]) == 5
        assert data["page"] == 1
        assert data["page_size"] == 5

    def test_get_log_by_id(self, client: TestClient, auth_headers, db_session, sample_medication, test_user):
        """Test getting a specific log by ID."""
        log = MedicationLog(
            medication_id=sample_medication.id,
            user_id=test_user.id,
            dose_taken="15mg",
            taken_at=datetime.utcnow(),
            notes="Test note"
        )
        db_session.add(log)
        db_session.commit()

        response = client.get(f"/api/logs/{log.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(log.id)
        assert data["dose_taken"] == "15mg"
        assert data["notes"] == "Test note"

    def test_get_log_not_found(self, client: TestClient, auth_headers):
        """Test getting non-existent log."""
        response = client.get(
            "/api/logs/00000000-0000-0000-0000-000000000000",
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_update_medication_log(self, client: TestClient, auth_headers, db_session, sample_medication, test_user):
        """Test updating a log entry."""
        log = MedicationLog(
            medication_id=sample_medication.id,
            user_id=test_user.id,
            dose_taken="10mg",
            taken_at=datetime.utcnow()
        )
        db_session.add(log)
        db_session.commit()

        response = client.put(
            f"/api/logs/{log.id}",
            headers=auth_headers,
            json={"dose_taken": "20mg", "notes": "Updated note"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["dose_taken"] == "20mg"
        assert data["notes"] == "Updated note"

    def test_update_log_future_time_fails(self, client: TestClient, auth_headers, db_session, sample_medication, test_user):
        """Test that updating with future time fails."""
        log = MedicationLog(
            medication_id=sample_medication.id,
            user_id=test_user.id,
            dose_taken="10mg",
            taken_at=datetime.utcnow()
        )
        db_session.add(log)
        db_session.commit()

        future_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        response = client.put(
            f"/api/logs/{log.id}",
            headers=auth_headers,
            json={"taken_at": future_time}
        )

        assert response.status_code == 422

    def test_delete_medication_log(self, client: TestClient, auth_headers, db_session, sample_medication, test_user):
        """Test deleting a log entry."""
        log = MedicationLog(
            medication_id=sample_medication.id,
            user_id=test_user.id,
            dose_taken="10mg",
            taken_at=datetime.utcnow()
        )
        db_session.add(log)
        db_session.commit()
        log_id = log.id

        response = client.delete(f"/api/logs/{log_id}", headers=auth_headers)

        assert response.status_code == 204

        # Verify deletion
        deleted_log = db_session.query(MedicationLog).filter_by(id=log_id).first()
        assert deleted_log is None

    def test_get_adherence_stats(self, client: TestClient, auth_headers, db_session, sample_medication, test_user):
        """Test getting adherence statistics."""
        # Create some logs
        for i in range(5):
            log = MedicationLog(
                medication_id=sample_medication.id,
                user_id=test_user.id,
                dose_taken="10mg",
                taken_at=datetime.utcnow() - timedelta(days=i)
            )
            db_session.add(log)
        db_session.commit()

        response = client.get("/api/logs/stats/adherence?days=7", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "total_medications" in data
        assert "total_logged_doses" in data
        assert "average_adherence" in data
        assert "medication_stats" in data
        assert len(data["medication_stats"]) >= 1

        # Check medication stats
        med_stat = data["medication_stats"][0]
        assert med_stat["medication_id"] == str(sample_medication.id)
        assert med_stat["medication_name"] == sample_medication.drug_name
        assert med_stat["total_logged_doses"] == 5
        assert "adherence_percentage" in med_stat

    def test_adherence_stats_filter_by_medication(self, client: TestClient, auth_headers, db_session, test_user):
        """Test adherence stats for specific medication."""
        # Create two medications
        med1 = Medication(user_id=test_user.id, drug_name="Med1", standard_dose="10mg", start_date=date.today(), active=True)
        med2 = Medication(user_id=test_user.id, drug_name="Med2", standard_dose="20mg", start_date=date.today(), active=True)
        db_session.add_all([med1, med2])
        db_session.commit()

        # Create logs only for med1
        for i in range(3):
            log = MedicationLog(
                medication_id=med1.id,
                user_id=test_user.id,
                dose_taken="10mg",
                taken_at=datetime.utcnow() - timedelta(days=i)
            )
            db_session.add(log)
        db_session.commit()

        response = client.get(f"/api/logs/stats/adherence?medication_id={med1.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total_medications"] == 1
        assert data["medication_stats"][0]["medication_id"] == str(med1.id)

    def test_user_cannot_access_others_logs(self, client: TestClient, db_session):
        """Test that users cannot access other users' logs."""
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

        # Create medication for user1
        med = Medication(
            user_id=user1.id,
            drug_name="User1 Med",
            standard_dose="10mg",
            start_date=date.today()
        )
        db_session.add(med)
        db_session.commit()

        # Create log for user1
        log = MedicationLog(
            medication_id=med.id,
            user_id=user1.id,
            dose_taken="10mg",
            taken_at=datetime.utcnow()
        )
        db_session.add(log)
        db_session.commit()

        # Login as user2
        login_response = client.post(
            "/api/auth/login",
            data={"username": "user2@example.com", "password": "password"}
        )
        user2_token = login_response.json()["access_token"]
        user2_headers = {"Authorization": f"Bearer {user2_token}"}

        # Try to access user1's log
        response = client.get(f"/api/logs/{log.id}", headers=user2_headers)
        assert response.status_code == 404

        # Try to get logs list (should be empty for user2)
        response = client.get("/api/logs/", headers=user2_headers)
        assert response.status_code == 200
        data = response.json()
        assert all(log_entry["user_id"] != str(user1.id) for log_entry in data["logs"])
