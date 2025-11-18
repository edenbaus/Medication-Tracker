"""Integration tests for dashboard API endpoints."""
import pytest
from datetime import datetime, timedelta
from app.models.medication import Medication, PrescriptionType
from app.models.medication_log import MedicationLog
from app.models.side_effect import SideEffect, SeverityLevel
from app.models.symptom import SymptomTracking
from app.models.third_party import ThirdParty


class TestDashboardAPI:
    """Integration tests for dashboard API endpoints."""

    def test_get_dashboard_summary_authenticated(self, client, auth_headers):
        """Test that dashboard summary requires authentication."""
        # Without authentication
        response = client.get("/api/dashboard/summary")
        assert response.status_code == 401

        # With authentication
        response = client.get("/api/dashboard/summary", headers=auth_headers)
        assert response.status_code == 200

    def test_dashboard_summary_structure(self, client, auth_headers):
        """Test that dashboard summary returns correct data structure."""
        response = client.get("/api/dashboard/summary", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Check all required fields exist
        required_fields = [
            "user_name",
            "total_active_medications",
            "total_logs_today",
            "total_logs_7days",
            "total_side_effects_7days",
            "total_symptoms_tracked_7days",
            "people_stats",
            "recent_activity",
            "medications_needing_attention"
        ]

        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        # Check data types
        assert isinstance(data["user_name"], str)
        assert isinstance(data["total_active_medications"], int)
        assert isinstance(data["total_logs_today"], int)
        assert isinstance(data["total_logs_7days"], int)
        assert isinstance(data["total_side_effects_7days"], int)
        assert isinstance(data["total_symptoms_tracked_7days"], int)
        assert isinstance(data["people_stats"], list)
        assert isinstance(data["recent_activity"], list)
        assert isinstance(data["medications_needing_attention"], list)

    def test_dashboard_people_stats_structure(self, client, auth_headers):
        """Test people_stats has correct structure."""
        response = client.get("/api/dashboard/summary", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Should have at least one person (Me)
        assert len(data["people_stats"]) >= 1

        person = data["people_stats"][0]
        assert "person_id" in person
        assert "person_name" in person
        assert "active_medications" in person
        assert "total_logs_7days" in person
        assert "side_effects_7days" in person
        assert "symptoms_tracked_7days" in person

        assert person["person_name"] == "Me"
        assert person["person_id"] is None  # Me has no person_id

    def test_dashboard_recent_activity_structure(self, client, auth_headers, test_user, db_session):
        """Test recent_activity has correct structure."""
        # Create some activity
        med = Medication(
            user_id=test_user.id,
            drug_name="Test Med",
            standard_dose="100mg",
            prescription_type=PrescriptionType.OTC,
            active=True
        )
        db_session.add(med)
        db_session.commit()
        db_session.refresh(med)

        log = MedicationLog(
            user_id=test_user.id,
            medication_id=med.id,
            taken_at=datetime.utcnow(),
            dose_taken="100mg"
        )
        db_session.add(log)
        db_session.commit()

        response = client.get("/api/dashboard/summary", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Should have activity
        assert len(data["recent_activity"]) > 0

        activity = data["recent_activity"][0]
        assert "id" in activity
        assert "activity_type" in activity
        assert "timestamp" in activity
        assert "description" in activity
        assert "person_name" in activity

        # Check activity type is valid
        assert activity["activity_type"] in ["log", "side_effect", "symptom", "medication_added"]

    def test_dashboard_medications_needing_attention_structure(self, client, auth_headers, test_user, db_session):
        """Test medications_needing_attention has correct structure."""
        # Create medication never logged
        med = Medication(
            user_id=test_user.id,
            drug_name="Never Logged",
            standard_dose="100mg",
            prescription_type=PrescriptionType.OTC,
            active=True
        )
        db_session.add(med)
        db_session.commit()

        response = client.get("/api/dashboard/summary", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Should have this medication in attention list
        assert len(data["medications_needing_attention"]) > 0

        med_attention = data["medications_needing_attention"][0]
        assert "medication_id" in med_attention
        assert "medication_name" in med_attention
        assert "last_logged" in med_attention
        assert "days_since_last_log" in med_attention
        assert "total_logs" in med_attention
        assert "is_active" in med_attention
        assert "person_name" in med_attention

    def test_dashboard_full_workflow(self, client, auth_headers, test_user, db_session):
        """Test complete dashboard workflow with all data types."""
        # Create third party
        child = ThirdParty(
            user_id=test_user.id,
            name="Child",
            relationship_type="child"
        )
        db_session.add(child)
        db_session.commit()
        db_session.refresh(child)

        # Create medications
        med_user = Medication(
            user_id=test_user.id,
            drug_name="User Med",
            standard_dose="100mg",
            prescription_type=PrescriptionType.LONG_TERM,
            active=True,
            third_party_id=None
        )
        med_child = Medication(
            user_id=test_user.id,
            drug_name="Child Med",
            standard_dose="50mg",
            prescription_type=PrescriptionType.SHORT_TERM,
            active=True,
            third_party_id=child.id
        )
        db_session.add_all([med_user, med_child])
        db_session.commit()
        db_session.refresh(med_user)
        db_session.refresh(med_child)

        now = datetime.utcnow()

        # Create logs
        log_user_today = MedicationLog(
            user_id=test_user.id,
            medication_id=med_user.id,
            taken_at=now,
            dose_taken="100mg"
        )
        log_child_week = MedicationLog(
            user_id=test_user.id,
            medication_id=med_child.id,
            taken_at=now - timedelta(days=2),
            dose_taken="50mg"
        )
        db_session.add_all([log_user_today, log_child_week])

        # Create side effect
        side_effect = SideEffect(
            user_id=test_user.id,
            medication_id=med_user.id,
            severity=SeverityLevel.MILD,
            description="Mild headache",
            occurred_at=now - timedelta(hours=1)
        )
        db_session.add(side_effect)

        # Create symptom
        symptom = SymptomTracking(
            user_id=test_user.id,
            medication_id=med_user.id,
            symptom_name="Pain",
            improvement_level=8,
            recorded_at=now - timedelta(hours=2)
        )
        db_session.add(symptom)

        db_session.commit()

        # Get dashboard
        response = client.get("/api/dashboard/summary", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Verify counts
        assert data["total_active_medications"] == 2
        assert data["total_logs_today"] == 1
        assert data["total_logs_7days"] == 2
        assert data["total_side_effects_7days"] == 1
        assert data["total_symptoms_tracked_7days"] == 1

        # Verify people stats (Me + Child)
        assert len(data["people_stats"]) == 2

        my_stats = next((p for p in data["people_stats"] if p["person_name"] == "Me"), None)
        assert my_stats is not None
        assert my_stats["active_medications"] == 1
        assert my_stats["total_logs_7days"] == 1

        child_stats = next((p for p in data["people_stats"] if p["person_name"] == "Child"), None)
        assert child_stats is not None
        assert child_stats["active_medications"] == 1
        assert child_stats["total_logs_7days"] == 1

        # Verify recent activity (should have 4 events: 2 logs, 1 side effect, 1 symptom)
        assert len(data["recent_activity"]) == 4
        activity_types = {a["activity_type"] for a in data["recent_activity"]}
        assert "log" in activity_types
        assert "side_effect" in activity_types
        assert "symptom" in activity_types

        # Count each type
        log_count = sum(1 for a in data["recent_activity"] if a["activity_type"] == "log")
        se_count = sum(1 for a in data["recent_activity"] if a["activity_type"] == "side_effect")
        sym_count = sum(1 for a in data["recent_activity"] if a["activity_type"] == "symptom")

        assert log_count == 2  # User log + Child log
        assert se_count == 1
        assert sym_count == 1

    def test_dashboard_isolates_users(self, client, auth_headers, test_user, db_session):
        """Test that dashboard only shows data for authenticated user."""
        from app.models.user import User
        from app.utils.security import get_password_hash

        # Create another user
        other_user = User(
            username="otheruser",
            email="other@example.com",
            password_hash=get_password_hash("password123")
        )
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)

        # Create medication for other user
        other_med = Medication(
            user_id=other_user.id,
            drug_name="Other User Med",
            standard_dose="200mg",
            prescription_type=PrescriptionType.OTC,
            active=True
        )
        db_session.add(other_med)
        db_session.commit()

        # Get dashboard for test_user
        response = client.get("/api/dashboard/summary", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Should not include other user's medication
        assert data["total_active_medications"] == 0

        # Medications needing attention should not include other user's meds
        med_names = [m["medication_name"] for m in data["medications_needing_attention"]]
        assert "Other User Med" not in med_names

    def test_dashboard_performance_with_large_dataset(self, client, auth_headers, test_user, db_session):
        """Test dashboard performance with many records."""
        # Create medication
        med = Medication(
            user_id=test_user.id,
            drug_name="Test Med",
            standard_dose="100mg",
            prescription_type=PrescriptionType.OTC,
            active=True
        )
        db_session.add(med)
        db_session.commit()
        db_session.refresh(med)

        now = datetime.utcnow()

        # Create many logs
        logs = []
        for i in range(100):
            log = MedicationLog(
                user_id=test_user.id,
                medication_id=med.id,
                taken_at=now - timedelta(days=i % 30),
                dose_taken="100mg"
            )
            logs.append(log)

        db_session.add_all(logs)
        db_session.commit()

        # Dashboard should still work and limit recent activity to 10
        response = client.get("/api/dashboard/summary", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Should limit recent activity
        assert len(data["recent_activity"]) <= 10

        # Should still count all logs correctly
        assert data["total_logs_7days"] > 0

    def test_dashboard_handles_inactive_medications(self, client, auth_headers, test_user, db_session):
        """Test that dashboard correctly handles inactive medications."""
        # Create active medication
        active_med = Medication(
            user_id=test_user.id,
            drug_name="Active Med",
            standard_dose="100mg",
            prescription_type=PrescriptionType.OTC,
            active=True
        )

        # Create inactive medication
        inactive_med = Medication(
            user_id=test_user.id,
            drug_name="Inactive Med",
            standard_dose="50mg",
            prescription_type=PrescriptionType.SHORT_TERM,
            active=False
        )

        db_session.add_all([active_med, inactive_med])
        db_session.commit()
        db_session.refresh(active_med)
        db_session.refresh(inactive_med)

        now = datetime.utcnow()

        # Create logs for both
        log_active = MedicationLog(
            user_id=test_user.id,
            medication_id=active_med.id,
            taken_at=now,
            dose_taken="100mg"
        )
        log_inactive = MedicationLog(
            user_id=test_user.id,
            medication_id=inactive_med.id,
            taken_at=now,
            dose_taken="50mg"
        )

        db_session.add_all([log_active, log_inactive])
        db_session.commit()

        response = client.get("/api/dashboard/summary", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Should only count active medication
        assert data["total_active_medications"] == 1

        # Should count logs for all medications (active and inactive)
        assert data["total_logs_today"] == 2

        # Medications needing attention should only include active meds
        med_names = [m["medication_name"] for m in data["medications_needing_attention"]]
        assert "Inactive Med" not in med_names

    def test_dashboard_timezone_handling(self, client, auth_headers, test_user, db_session):
        """Test that dashboard handles UTC timestamps correctly."""
        # Create medication
        med = Medication(
            user_id=test_user.id,
            drug_name="Test Med",
            standard_dose="100mg",
            prescription_type=PrescriptionType.OTC,
            active=True
        )
        db_session.add(med)
        db_session.commit()
        db_session.refresh(med)

        # Create log with specific UTC time
        specific_time = datetime(2025, 11, 18, 10, 30, 0)
        log = MedicationLog(
            user_id=test_user.id,
            medication_id=med.id,
            taken_at=specific_time,
            dose_taken="100mg"
        )
        db_session.add(log)
        db_session.commit()

        response = client.get("/api/dashboard/summary", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Check recent activity has the log
        if len(data["recent_activity"]) > 0:
            log_activity = next((a for a in data["recent_activity"] if a["activity_type"] == "log"), None)
            if log_activity:
                # Timestamp should be returned as ISO format string
                assert "timestamp" in log_activity
                assert isinstance(log_activity["timestamp"], str)
