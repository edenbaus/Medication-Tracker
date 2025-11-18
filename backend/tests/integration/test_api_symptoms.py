"""Integration tests for Symptoms API endpoints."""
import pytest
from datetime import datetime


class TestSymptomsAPI:
    """Test symptoms API endpoints."""

    def test_create_symptom(self, client, auth_headers, test_medication):
        """Test creating a symptom tracking entry."""
        data = {
            "medication_id": str(test_medication.id),
            "symptom_name": "Pain Level",
            "improvement_level": 8,
            "recorded_at": datetime.utcnow().isoformat()
        }

        response = client.post("/api/symptoms", json=data, headers=auth_headers)

        assert response.status_code == 201
        result = response.json()
        assert result["symptom_name"] == "Pain Level"
        assert result["improvement_level"] == 8
        assert result["medication_id"] == str(test_medication.id)

    def test_create_symptom_invalid_improvement_level(self, client, auth_headers, test_medication):
        """Test creating symptom with invalid improvement level."""
        data = {
            "medication_id": str(test_medication.id),
            "symptom_name": "Pain",
            "improvement_level": 11,  # Should be 0-10
            "recorded_at": datetime.utcnow().isoformat()
        }

        response = client.post("/api/symptoms", json=data, headers=auth_headers)

        assert response.status_code == 422

    def test_list_symptoms(self, client, auth_headers, test_symptom):
        """Test listing symptoms."""
        response = client.get("/api/symptoms", headers=auth_headers)

        assert response.status_code == 200
        result = response.json()
        assert len(result) >= 1
        assert any(s["id"] == str(test_symptom.id) for s in result)

    def test_get_symptom(self, client, auth_headers, test_symptom):
        """Test getting a specific symptom."""
        response = client.get(
            f"/api/symptoms/{test_symptom.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        result = response.json()
        assert result["id"] == str(test_symptom.id)
        assert result["symptom_name"] == test_symptom.symptom_name

    def test_get_symptom_not_found(self, client, auth_headers):
        """Test getting non-existent symptom."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/symptoms/{fake_id}", headers=auth_headers)

        assert response.status_code == 404

    def test_update_symptom(self, client, auth_headers, test_symptom):
        """Test updating a symptom."""
        data = {
            "symptom_name": "Updated Symptom",
            "improvement_level": 9
        }

        response = client.put(
            f"/api/symptoms/{test_symptom.id}",
            json=data,
            headers=auth_headers
        )

        assert response.status_code == 200
        result = response.json()
        assert result["symptom_name"] == "Updated Symptom"
        assert result["improvement_level"] == 9

    def test_delete_symptom(self, client, auth_headers, test_symptom):
        """Test deleting a symptom."""
        response = client.delete(
            f"/api/symptoms/{test_symptom.id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verify deletion
        get_response = client.get(
            f"/api/symptoms/{test_symptom.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    def test_filter_symptoms_by_medication(self, client, auth_headers, db_session, test_user, test_medication):
        """Test filtering symptoms by medication."""
        from tests.factories.factories import MedicationFactory, SymptomFactory

        # Create another medication and symptom
        other_med = MedicationFactory.create(db_session, test_user, drug_name="Other Med")
        s1 = SymptomFactory.create(db_session, test_user, test_medication, symptom_name="S1")
        s2 = SymptomFactory.create(db_session, test_user, other_med, symptom_name="S2")

        response = client.get(
            f"/api/symptoms?medication_id={test_medication.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result) >= 1
        assert all(s["medication_id"] == str(test_medication.id) for s in result)

    def test_track_symptom_improvement_over_time(self, client, auth_headers, db_session, test_user, test_medication):
        """Test tracking symptom improvement over multiple entries."""
        from tests.factories.factories import SymptomFactory
        from datetime import timedelta

        # Create symptom entries showing improvement
        base_time = datetime.utcnow()
        s1 = SymptomFactory.create(
            db_session, test_user, test_medication,
            symptom_name="Headache", improvement_level=3,
            recorded_at=base_time - timedelta(days=7)
        )
        s2 = SymptomFactory.create(
            db_session, test_user, test_medication,
            symptom_name="Headache", improvement_level=6,
            recorded_at=base_time - timedelta(days=3)
        )
        s3 = SymptomFactory.create(
            db_session, test_user, test_medication,
            symptom_name="Headache", improvement_level=8,
            recorded_at=base_time
        )

        response = client.get(
            f"/api/symptoms?medication_id={test_medication.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        result = response.json()
        headaches = [s for s in result if s["symptom_name"] == "Headache"]
        assert len(headaches) == 3

        # Verify they're showing improvement
        levels = sorted([s["improvement_level"] for s in headaches])
        assert levels == [3, 6, 8]

    def test_unauthorized_access(self, client):
        """Test accessing symptoms without authentication."""
        response = client.get("/api/symptoms")
        assert response.status_code == 401

    def test_cannot_access_other_user_symptom(self, client, db_session, auth_headers):
        """Test that users cannot access other users' symptoms."""
        from tests.factories.factories import UserFactory, MedicationFactory, SymptomFactory

        # Create another user and their symptom
        other_user = UserFactory.create(
            db_session,
            username="otheruser",
            email="other@example.com"
        )
        other_med = MedicationFactory.create(db_session, other_user)
        other_symptom = SymptomFactory.create(db_session, other_user, other_med)

        response = client.get(
            f"/api/symptoms/{other_symptom.id}",
            headers=auth_headers
        )

        assert response.status_code == 404
