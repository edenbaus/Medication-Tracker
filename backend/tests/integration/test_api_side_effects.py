"""Integration tests for Side Effects API endpoints."""
import pytest
from datetime import datetime, timedelta


class TestSideEffectsAPI:
    """Test side effects API endpoints."""

    def test_create_side_effect(self, client, auth_headers, test_medication):
        """Test creating a side effect."""
        data = {
            "medication_id": str(test_medication.id),
            "description": "Nausea",
            "severity": "moderate",
            "occurred_at": datetime.utcnow().isoformat()
        }

        response = client.post("/api/side-effects", json=data, headers=auth_headers)

        assert response.status_code == 201
        result = response.json()
        assert result["description"] == "Nausea"
        assert result["severity"] == "moderate"
        assert result["medication_id"] == str(test_medication.id)

    def test_create_side_effect_invalid_severity(self, client, auth_headers, test_medication):
        """Test creating side effect with invalid severity."""
        data = {
            "medication_id": str(test_medication.id),
            "description": "Headache",
            "severity": "invalid",
            "occurred_at": datetime.utcnow().isoformat()
        }

        response = client.post("/api/side-effects", json=data, headers=auth_headers)

        assert response.status_code == 422

    def test_list_side_effects(self, client, auth_headers, test_side_effect):
        """Test listing side effects."""
        response = client.get("/api/side-effects", headers=auth_headers)

        assert response.status_code == 200
        result = response.json()
        assert len(result) >= 1
        assert any(se["id"] == str(test_side_effect.id) for se in result)

    def test_get_side_effect(self, client, auth_headers, test_side_effect):
        """Test getting a specific side effect."""
        response = client.get(
            f"/api/side-effects/{test_side_effect.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        result = response.json()
        assert result["id"] == str(test_side_effect.id)
        assert result["description"] == test_side_effect.description

    def test_get_side_effect_not_found(self, client, auth_headers):
        """Test getting non-existent side effect."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/side-effects/{fake_id}", headers=auth_headers)

        assert response.status_code == 404

    def test_update_side_effect(self, client, auth_headers, test_side_effect):
        """Test updating a side effect."""
        data = {
            "description": "Updated description",
            "severity": "severe"
        }

        response = client.put(
            f"/api/side-effects/{test_side_effect.id}",
            json=data,
            headers=auth_headers
        )

        assert response.status_code == 200
        result = response.json()
        assert result["description"] == "Updated description"
        assert result["severity"] == "severe"

    def test_delete_side_effect(self, client, auth_headers, test_side_effect):
        """Test deleting a side effect."""
        response = client.delete(
            f"/api/side-effects/{test_side_effect.id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verify deletion
        get_response = client.get(
            f"/api/side-effects/{test_side_effect.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    def test_filter_side_effects_by_medication(self, client, auth_headers, db_session, test_user, test_medication):
        """Test filtering side effects by medication."""
        from tests.factories.factories import MedicationFactory, SideEffectFactory

        # Create another medication and side effect
        other_med = MedicationFactory.create(db_session, test_user, drug_name="Other Med")
        se1 = SideEffectFactory.create(db_session, test_user, test_medication, description="SE1")
        se2 = SideEffectFactory.create(db_session, test_user, other_med, description="SE2")

        response = client.get(
            f"/api/side-effects?medication_id={test_medication.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result) >= 1
        assert all(se["medication_id"] == str(test_medication.id) for se in result)

    def test_filter_side_effects_by_severity(self, client, auth_headers, db_session, test_user, test_medication):
        """Test filtering side effects by severity."""
        from tests.factories.factories import SideEffectFactory

        se_mild = SideEffectFactory.create(
            db_session, test_user, test_medication,
            description="Mild SE", severity="mild"
        )
        se_severe = SideEffectFactory.create(
            db_session, test_user, test_medication,
            description="Severe SE", severity="severe"
        )

        response = client.get("/api/side-effects?severity=mild", headers=auth_headers)

        assert response.status_code == 200
        result = response.json()
        assert all(se["severity"] == "mild" for se in result)

    def test_unauthorized_access(self, client):
        """Test accessing side effects without authentication."""
        response = client.get("/api/side-effects")
        assert response.status_code == 401

    def test_cannot_access_other_user_side_effect(self, client, db_session, auth_headers):
        """Test that users cannot access other users' side effects."""
        from tests.factories.factories import UserFactory, MedicationFactory, SideEffectFactory

        # Create another user and their side effect
        other_user = UserFactory.create(
            db_session,
            username="otheruser",
            email="other@example.com"
        )
        other_med = MedicationFactory.create(db_session, other_user)
        other_se = SideEffectFactory.create(db_session, other_user, other_med)

        response = client.get(
            f"/api/side-effects/{other_se.id}",
            headers=auth_headers
        )

        assert response.status_code == 404
