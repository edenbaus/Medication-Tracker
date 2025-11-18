"""Unit tests for dashboard functionality."""
import pytest
from datetime import datetime, timedelta
from app.models.user import User
from app.models.medication import Medication, PrescriptionType
from app.models.medication_log import MedicationLog
from app.models.side_effect import SideEffect, SeverityLevel
from app.models.symptom import SymptomTracking
from app.models.third_party import ThirdParty
from app.utils.security import get_password_hash


class TestDashboardEndpoint:
    """Test dashboard API endpoint."""

    def test_dashboard_with_no_data(self, client, auth_headers):
        """Test dashboard returns successfully with no medications or logs."""
        response = client.get("/api/dashboard/summary", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Should have user name (regression test for full_name bug)
        assert "user_name" in data
        assert data["user_name"] in ["testuser", "test@example.com"]

        # All counts should be zero
        assert data["total_active_medications"] == 0
        assert data["total_logs_today"] == 0
        assert data["total_logs_7days"] == 0
        assert data["total_side_effects_7days"] == 0
        assert data["total_symptoms_tracked_7days"] == 0

        # Should have empty lists
        assert data["recent_activity"] == []
        assert data["medications_needing_attention"] == []

        # Should have at least "Me" in people stats
        assert len(data["people_stats"]) >= 1
        assert data["people_stats"][0]["person_name"] == "Me"

    def test_dashboard_user_name_uses_username(self, client, auth_headers):
        """Test that dashboard uses username attribute, not full_name.

        Regression test for: AttributeError: 'User' object has no attribute 'full_name'
        """
        response = client.get("/api/dashboard/summary", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Should use username from User model (username or email)
        assert "user_name" in data
        # Username should be either the username field or email field
        assert data["user_name"] in ["testuser", "test@example.com"]

    def test_dashboard_with_active_medications(self, client, auth_headers, test_user, db_session):
        """Test dashboard counts active medications correctly.

        Regression test for: AttributeError: type object 'Medication' has no attribute 'is_active'
        """
        # Create active medications
        med1 = Medication(
            user_id=test_user.id,
            drug_name="Aspirin",
            standard_dose="100mg",
            prescription_type=PrescriptionType.OTC,
            active=True  # Using 'active', not 'is_active'
        )
        med2 = Medication(
            user_id=test_user.id,
            drug_name="Ibuprofen",
            standard_dose="200mg",
            prescription_type=PrescriptionType.OTC,
            active=True
        )
        # Create inactive medication (should not be counted)
        med3 = Medication(
            user_id=test_user.id,
            drug_name="Old Med",
            standard_dose="50mg",
            prescription_type=PrescriptionType.SHORT_TERM,
            active=False
        )

        db_session.add_all([med1, med2, med3])
        db_session.commit()

        response = client.get("/api/dashboard/summary", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Should only count active medications
        assert data["total_active_medications"] == 2

    def test_dashboard_with_medication_logs(self, client, auth_headers, test_user, db_session):
        """Test dashboard counts medication logs correctly.

        Regression test for: AttributeError: type object 'MedicationLog' has no attribute 'logged_at'
        """
        # Create medication
        med = Medication(
            user_id=test_user.id,
            drug_name="Aspirin",
            standard_dose="100mg",
            prescription_type=PrescriptionType.OTC,
            active=True
        )
        db_session.add(med)
        db_session.commit()
        db_session.refresh(med)

        now = datetime.utcnow()
        today_start = datetime(now.year, now.month, now.day)

        # Create logs for today
        log1 = MedicationLog(
            user_id=test_user.id,
            medication_id=med.id,
            taken_at=now,  # Using 'taken_at', not 'logged_at'
            dose_taken="100mg"
        )
        log2 = MedicationLog(
            user_id=test_user.id,
            medication_id=med.id,
            taken_at=now - timedelta(hours=2),
            dose_taken="100mg"
        )

        # Create log from 5 days ago (should count in 7 days but not today)
        log3 = MedicationLog(
            user_id=test_user.id,
            medication_id=med.id,
            taken_at=now - timedelta(days=5),
            dose_taken="100mg"
        )

        # Create log from 10 days ago (should not count)
        log4 = MedicationLog(
            user_id=test_user.id,
            medication_id=med.id,
            taken_at=now - timedelta(days=10),
            dose_taken="100mg"
        )

        db_session.add_all([log1, log2, log3, log4])
        db_session.commit()

        response = client.get("/api/dashboard/summary", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Should count logs correctly using taken_at
        assert data["total_logs_today"] == 2
        assert data["total_logs_7days"] == 3

    def test_dashboard_medications_needing_attention(self, client, auth_headers, test_user, db_session):
        """Test medications needing attention are identified correctly."""
        # Create medication not logged recently
        med1 = Medication(
            user_id=test_user.id,
            drug_name="Aspirin",
            standard_dose="100mg",
            prescription_type=PrescriptionType.OTC,
            active=True
        )
        # Create medication logged recently
        med2 = Medication(
            user_id=test_user.id,
            drug_name="Ibuprofen",
            standard_dose="200mg",
            prescription_type=PrescriptionType.OTC,
            active=True
        )
        # Create medication never logged
        med3 = Medication(
            user_id=test_user.id,
            drug_name="Vitamin D",
            standard_dose="1000 IU",
            prescription_type=PrescriptionType.OTC,
            active=True
        )

        db_session.add_all([med1, med2, med3])
        db_session.commit()
        db_session.refresh(med1)
        db_session.refresh(med2)

        now = datetime.utcnow()

        # Log for med1 from 5 days ago (needs attention)
        log1 = MedicationLog(
            user_id=test_user.id,
            medication_id=med1.id,
            taken_at=now - timedelta(days=5),
            dose_taken="100mg"
        )

        # Log for med2 from 1 day ago (doesn't need attention)
        log2 = MedicationLog(
            user_id=test_user.id,
            medication_id=med2.id,
            taken_at=now - timedelta(days=1),
            dose_taken="200mg"
        )

        # med3 has no logs at all (needs attention)

        db_session.add_all([log1, log2])
        db_session.commit()

        response = client.get("/api/dashboard/summary", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Should have 2 medications needing attention (Aspirin and Vitamin D)
        assert len(data["medications_needing_attention"]) == 2

        # Check that med1 is in the list
        med1_data = next((m for m in data["medications_needing_attention"] if m["medication_name"] == "Aspirin"), None)
        assert med1_data is not None
        assert med1_data["days_since_last_log"] == 5

        # Check that med3 (never logged) is in the list
        med3_data = next((m for m in data["medications_needing_attention"] if m["medication_name"] == "Vitamin D"), None)
        assert med3_data is not None
        assert med3_data["last_logged"] is None
        assert med3_data["days_since_last_log"] is None

    def test_dashboard_recent_activity_timeline(self, client, auth_headers, test_user, db_session):
        """Test recent activity timeline includes all event types."""
        # Create medication
        med = Medication(
            user_id=test_user.id,
            drug_name="Aspirin",
            standard_dose="100mg",
            prescription_type=PrescriptionType.OTC,
            active=True
        )
        db_session.add(med)
        db_session.commit()
        db_session.refresh(med)

        now = datetime.utcnow()

        # Create different types of activities
        log = MedicationLog(
            user_id=test_user.id,
            medication_id=med.id,
            taken_at=now - timedelta(hours=1),
            dose_taken="100mg"
        )

        side_effect = SideEffect(
            user_id=test_user.id,
            medication_id=med.id,
            severity=SeverityLevel.MILD,
            description="Mild headache",
            occurred_at=now - timedelta(hours=2)
        )

        symptom = SymptomTracking(
            user_id=test_user.id,
            medication_id=med.id,
            symptom_name="Pain",
            improvement_level=7,
            recorded_at=now - timedelta(hours=3)
        )

        db_session.add_all([log, side_effect, symptom])
        db_session.commit()

        response = client.get("/api/dashboard/summary", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Should have 3 recent activities
        assert len(data["recent_activity"]) == 3

        # Check activity types
        activity_types = [a["activity_type"] for a in data["recent_activity"]]
        assert "log" in activity_types
        assert "side_effect" in activity_types
        assert "symptom" in activity_types

        # Activities should be sorted by timestamp (newest first)
        timestamps = [datetime.fromisoformat(a["timestamp"].replace('Z', '+00:00')) for a in data["recent_activity"]]
        assert timestamps == sorted(timestamps, reverse=True)

    def test_dashboard_multi_person_stats(self, client, auth_headers, test_user, db_session):
        """Test dashboard shows per-person statistics."""
        # Create third party
        child = ThirdParty(
            user_id=test_user.id,
            name="Child",
            relationship_type="child"
        )
        db_session.add(child)
        db_session.commit()
        db_session.refresh(child)

        # Create medication for user
        med1 = Medication(
            user_id=test_user.id,
            drug_name="Aspirin",
            standard_dose="100mg",
            prescription_type=PrescriptionType.OTC,
            active=True,
            third_party_id=None  # For user
        )

        # Create medication for child
        med2 = Medication(
            user_id=test_user.id,
            drug_name="Children's Tylenol",
            standard_dose="5ml",
            prescription_type=PrescriptionType.OTC,
            active=True,
            third_party_id=child.id
        )

        db_session.add_all([med1, med2])
        db_session.commit()

        response = client.get("/api/dashboard/summary", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Should have stats for 2 people
        assert len(data["people_stats"]) == 2

        # Check user stats
        my_stats = next((p for p in data["people_stats"] if p["person_name"] == "Me"), None)
        assert my_stats is not None
        assert my_stats["active_medications"] == 1

        # Check child stats
        child_stats = next((p for p in data["people_stats"] if p["person_name"] == "Child"), None)
        assert child_stats is not None
        assert child_stats["active_medications"] == 1

    def test_dashboard_with_side_effects_and_symptoms(self, client, auth_headers, test_user, db_session):
        """Test dashboard counts side effects and symptoms correctly."""
        # Create medication
        med = Medication(
            user_id=test_user.id,
            drug_name="Aspirin",
            standard_dose="100mg",
            prescription_type=PrescriptionType.OTC,
            active=True
        )
        db_session.add(med)
        db_session.commit()
        db_session.refresh(med)

        now = datetime.utcnow()

        # Create side effects in last 7 days
        se1 = SideEffect(
            user_id=test_user.id,
            medication_id=med.id,
            severity=SeverityLevel.MILD,
            description="Headache",
            occurred_at=now - timedelta(days=2)
        )
        se2 = SideEffect(
            user_id=test_user.id,
            medication_id=med.id,
            severity=SeverityLevel.MODERATE,
            description="Nausea",
            occurred_at=now - timedelta(days=5)
        )

        # Side effect from 10 days ago (should not count)
        se3 = SideEffect(
            user_id=test_user.id,
            medication_id=med.id,
            severity=SeverityLevel.MILD,
            description="Old issue",
            occurred_at=now - timedelta(days=10)
        )

        # Create symptoms in last 7 days
        sym1 = SymptomTracking(
            user_id=test_user.id,
            medication_id=med.id,
            symptom_name="Pain",
            improvement_level=7,
            recorded_at=now - timedelta(days=1)
        )
        sym2 = SymptomTracking(
            user_id=test_user.id,
            medication_id=med.id,
            symptom_name="Inflammation",
            improvement_level=8,
            recorded_at=now - timedelta(days=3)
        )

        db_session.add_all([se1, se2, se3, sym1, sym2])
        db_session.commit()

        response = client.get("/api/dashboard/summary", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Should count only those in last 7 days
        assert data["total_side_effects_7days"] == 2
        assert data["total_symptoms_tracked_7days"] == 2


class TestDashboardModelAttributes:
    """Test that models have correct attributes (regression tests)."""

    def test_user_model_has_username_not_fullname(self, db_session, test_user):
        """Test User model uses 'username' attribute, not 'full_name'.

        Regression test for: AttributeError: 'User' object has no attribute 'full_name'
        """
        # User should have username attribute
        assert hasattr(test_user, 'username')
        assert test_user.username == "testuser"

        # User should have email attribute
        assert hasattr(test_user, 'email')
        assert test_user.email == "test@example.com"

        # User should NOT have full_name attribute
        assert not hasattr(test_user, 'full_name')

    def test_medication_model_has_active_not_is_active(self, db_session, test_user):
        """Test Medication model uses 'active' attribute, not 'is_active'.

        Regression test for: AttributeError: type object 'Medication' has no attribute 'is_active'
        """
        med = Medication(
            user_id=test_user.id,
            drug_name="Aspirin",
            standard_dose="100mg",
            prescription_type=PrescriptionType.OTC,
            active=True
        )
        db_session.add(med)
        db_session.commit()
        db_session.refresh(med)

        # Medication should have 'active' attribute
        assert hasattr(med, 'active')
        assert med.active is True

        # Medication should NOT have 'is_active' attribute
        assert not hasattr(med, 'is_active')

    def test_medication_log_model_has_taken_at_not_logged_at(self, db_session, test_user):
        """Test MedicationLog model uses 'taken_at' attribute, not 'logged_at'.

        Regression test for: AttributeError: type object 'MedicationLog' has no attribute 'logged_at'
        """
        # Create medication first
        med = Medication(
            user_id=test_user.id,
            drug_name="Aspirin",
            standard_dose="100mg",
            prescription_type=PrescriptionType.OTC,
            active=True
        )
        db_session.add(med)
        db_session.commit()
        db_session.refresh(med)

        # Create log
        now = datetime.utcnow()
        log = MedicationLog(
            user_id=test_user.id,
            medication_id=med.id,
            taken_at=now,
            dose_taken="100mg"
        )
        db_session.add(log)
        db_session.commit()
        db_session.refresh(log)

        # Log should have 'taken_at' attribute
        assert hasattr(log, 'taken_at')
        assert log.taken_at == now

        # Log should NOT have 'logged_at' attribute
        assert not hasattr(log, 'logged_at')

    def test_medication_model_column_names(self):
        """Test Medication model has correct column names."""
        from app.models.medication import Medication

        # Check that the class has the correct attribute
        assert hasattr(Medication, 'active')
        assert not hasattr(Medication, 'is_active')

    def test_medication_log_model_column_names(self):
        """Test MedicationLog model has correct column names."""
        from app.models.medication_log import MedicationLog

        # Check that the class has the correct attribute
        assert hasattr(MedicationLog, 'taken_at')
        assert not hasattr(MedicationLog, 'logged_at')

    def test_user_model_column_names(self):
        """Test User model has correct column names."""
        from app.models.user import User

        # Check that the class has the correct attributes
        assert hasattr(User, 'username')
        assert hasattr(User, 'email')
        assert not hasattr(User, 'full_name')
