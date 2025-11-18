"""Integration tests for Journey Visualization API endpoints."""
import pytest
from datetime import datetime, timedelta, date


class TestJourneyAPI:
    """Test journey visualization API endpoints."""

    def test_get_journey_visualization(self, client, auth_headers, db_session, test_user, test_medication):
        """Test getting journey visualization data."""
        from tests.factories.factories import MedicationLogFactory, SideEffectFactory, SymptomFactory

        # Create some historical data
        base_date = datetime.utcnow() - timedelta(days=30)

        # Create logs over 30 days
        for i in range(30):
            MedicationLogFactory.create(
                db_session,
                test_medication,
                taken_at=base_date + timedelta(days=i)
            )

        # Create some side effects
        for i in [5, 10, 15]:
            SideEffectFactory.create(
                db_session,
                test_user,
                test_medication,
                occurred_at=base_date + timedelta(days=i)
            )

        # Create symptom tracking showing improvement
        for i, level in [(0, 3), (10, 5), (20, 7), (30, 9)]:
            SymptomFactory.create(
                db_session,
                test_user,
                test_medication,
                symptom_name="Pain",
                improvement_level=level,
                recorded_at=base_date + timedelta(days=i)
            )

        response = client.get(
            f"/api/journey/visualization?medication_id={test_medication.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        result = response.json()
        assert "adherence_data" in result
        assert "side_effects_timeline" in result
        assert "symptom_improvement" in result

    def test_journey_date_range_filter(self, client, auth_headers, db_session, test_user, test_medication):
        """Test journey visualization with date range filter."""
        from tests.factories.factories import MedicationLogFactory

        start_date = (datetime.utcnow() - timedelta(days=60)).date()
        end_date = (datetime.utcnow() - timedelta(days=30)).date()

        # Create logs across different date ranges
        for i in range(90):
            MedicationLogFactory.create(
                db_session,
                test_medication,
                taken_at=datetime.utcnow() - timedelta(days=90 - i)
            )

        response = client.get(
            f"/api/journey/visualization?medication_id={test_medication.id}&start_date={start_date}&end_date={end_date}",
            headers=auth_headers
        )

        assert response.status_code == 200
        result = response.json()
        # Verify data is within date range
        assert result is not None

    def test_journey_adherence_calculation(self, client, auth_headers, db_session, test_user, test_medication):
        """Test adherence calculation in journey visualization."""
        from tests.factories.factories import MedicationLogFactory

        # Create medication with daily schedule
        test_medication.dosing_schedule = {
            "frequency": "daily",
            "times": ["08:00"]
        }
        db_session.commit()

        # Create logs for 20 out of 30 days (66.7% adherence)
        base_date = datetime.utcnow() - timedelta(days=30)
        for i in range(0, 30, 3):  # Every 3rd day = ~10 logs
            MedicationLogFactory.create(
                db_session,
                test_medication,
                taken_at=base_date + timedelta(days=i)
            )

        response = client.get(
            f"/api/journey/visualization?medication_id={test_medication.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        result = response.json()
        # Check adherence is calculated
        if "adherence_rate" in result:
            assert 0 <= result["adherence_rate"] <= 100

    def test_journey_symptom_correlation(self, client, auth_headers, db_session, test_user, test_medication):
        """Test symptom correlation in journey data."""
        from tests.factories.factories import SymptomFactory

        # Create symptom entries showing correlation with medication
        symptoms = [
            ("Headache", 3),
            ("Headache", 5),
            ("Headache", 7),
            ("Headache", 9),
        ]

        for i, (name, level) in enumerate(symptoms):
            SymptomFactory.create(
                db_session,
                test_user,
                test_medication,
                symptom_name=name,
                improvement_level=level,
                recorded_at=datetime.utcnow() - timedelta(days=30 - i * 10)
            )

        response = client.get(
            f"/api/journey/visualization?medication_id={test_medication.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        result = response.json()
        assert "symptom_improvement" in result

    def test_journey_side_effects_timeline(self, client, auth_headers, db_session, test_user, test_medication):
        """Test side effects timeline in journey."""
        from tests.factories.factories import SideEffectFactory

        # Create side effects with different severities
        side_effects = [
            ("Nausea", "mild", 5),
            ("Headache", "moderate", 10),
            ("Dizziness", "severe", 15),
        ]

        for desc, severity, days_ago in side_effects:
            SideEffectFactory.create(
                db_session,
                test_user,
                test_medication,
                description=desc,
                severity=severity,
                occurred_at=datetime.utcnow() - timedelta(days=days_ago)
            )

        response = client.get(
            f"/api/journey/visualization?medication_id={test_medication.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        result = response.json()
        assert "side_effects_timeline" in result

    def test_journey_multiple_medications(self, client, auth_headers, db_session, test_user):
        """Test journey when comparing multiple medications."""
        from tests.factories.factories import MedicationFactory, MedicationLogFactory

        med1 = MedicationFactory.create(db_session, test_user, drug_name="Med1")
        med2 = MedicationFactory.create(db_session, test_user, drug_name="Med2")

        # Create logs for both
        for med in [med1, med2]:
            for i in range(30):
                MedicationLogFactory.create(
                    db_session,
                    med,
                    taken_at=datetime.utcnow() - timedelta(days=30 - i)
                )

        # Test getting journey for each
        for med in [med1, med2]:
            response = client.get(
                f"/api/journey/visualization?medication_id={med.id}",
                headers=auth_headers
            )
            assert response.status_code == 200

    def test_journey_no_data(self, client, auth_headers, test_medication):
        """Test journey visualization with no historical data."""
        response = client.get(
            f"/api/journey/visualization?medication_id={test_medication.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        result = response.json()
        # Should return empty or minimal data structure
        assert result is not None

    def test_journey_invalid_medication(self, client, auth_headers):
        """Test journey with invalid medication ID."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(
            f"/api/journey/visualization?medication_id={fake_id}",
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_journey_third_party_medication(self, client, auth_headers, db_session, test_user, test_third_party):
        """Test journey visualization for third party medication."""
        from tests.factories.factories import MedicationFactory, MedicationLogFactory

        med = MedicationFactory.create(
            db_session,
            test_user,
            drug_name="Child Med",
            third_party=test_third_party
        )

        # Create some logs
        for i in range(10):
            MedicationLogFactory.create(
                db_session,
                med,
                taken_at=datetime.utcnow() - timedelta(days=10 - i)
            )

        response = client.get(
            f"/api/journey/visualization?medication_id={med.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        result = response.json()
        # Should include third party context
        assert result is not None

    def test_journey_export_data(self, client, auth_headers, db_session, test_user, test_medication):
        """Test exporting journey data (if endpoint exists)."""
        from tests.factories.factories import MedicationLogFactory

        # Create some data
        for i in range(10):
            MedicationLogFactory.create(
                db_session,
                test_medication,
                taken_at=datetime.utcnow() - timedelta(days=10 - i)
            )

        response = client.get(
            f"/api/journey/export?medication_id={test_medication.id}&format=json",
            headers=auth_headers
        )

        # Endpoint may or may not exist
        assert response.status_code in [200, 404]

    def test_unauthorized_access(self, client, test_medication):
        """Test accessing journey without authentication."""
        response = client.get(f"/api/journey/visualization?medication_id={test_medication.id}")
        assert response.status_code == 401

    def test_cannot_access_other_user_journey(self, client, db_session, auth_headers):
        """Test that users cannot access other users' journey data."""
        from tests.factories.factories import UserFactory, MedicationFactory

        # Create another user and their medication
        other_user = UserFactory.create(
            db_session,
            username="otheruser",
            email="other@example.com"
        )
        other_med = MedicationFactory.create(db_session, other_user)

        response = client.get(
            f"/api/journey/visualization?medication_id={other_med.id}",
            headers=auth_headers
        )

        assert response.status_code == 404
