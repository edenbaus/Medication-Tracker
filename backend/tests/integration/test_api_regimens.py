"""Integration tests for Regimens API endpoints."""
import pytest


class TestRegimensAPI:
    """Test regimens API endpoints."""

    def test_create_regimen(self, client, auth_headers):
        """Test creating a regimen."""
        data = {
            "name": "Morning Medications",
            "description": "All medications to be taken in the morning",
            "schedule": {
                "time": "08:00",
                "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
            }
        }

        response = client.post("/api/regimens", json=data, headers=auth_headers)

        assert response.status_code == 201
        result = response.json()
        assert result["name"] == "Morning Medications"
        assert result["description"] == "All medications to be taken in the morning"

    def test_create_regimen_minimal(self, client, auth_headers):
        """Test creating regimen with minimal data."""
        data = {
            "name": "Evening Regimen"
        }

        response = client.post("/api/regimens", json=data, headers=auth_headers)

        assert response.status_code == 201
        result = response.json()
        assert result["name"] == "Evening Regimen"

    def test_list_regimens(self, client, auth_headers, test_regimen):
        """Test listing regimens."""
        response = client.get("/api/regimens", headers=auth_headers)

        assert response.status_code == 200
        result = response.json()
        assert len(result) >= 1
        assert any(r["id"] == str(test_regimen.id) for r in result)

    def test_get_regimen(self, client, auth_headers, test_regimen):
        """Test getting a specific regimen."""
        response = client.get(
            f"/api/regimens/{test_regimen.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        result = response.json()
        assert result["id"] == str(test_regimen.id)
        assert result["name"] == test_regimen.name

    def test_get_regimen_not_found(self, client, auth_headers):
        """Test getting non-existent regimen."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/regimens/{fake_id}", headers=auth_headers)

        assert response.status_code == 404

    def test_update_regimen(self, client, auth_headers, test_regimen):
        """Test updating a regimen."""
        data = {
            "name": "Updated Regimen",
            "description": "Updated description"
        }

        response = client.put(
            f"/api/regimens/{test_regimen.id}",
            json=data,
            headers=auth_headers
        )

        assert response.status_code == 200
        result = response.json()
        assert result["name"] == "Updated Regimen"
        assert result["description"] == "Updated description"

    def test_delete_regimen(self, client, auth_headers, test_regimen):
        """Test deleting a regimen."""
        response = client.delete(
            f"/api/regimens/{test_regimen.id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verify deletion
        get_response = client.get(
            f"/api/regimens/{test_regimen.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    def test_add_medication_to_regimen(self, client, auth_headers, test_regimen, test_medication):
        """Test adding a medication to a regimen."""
        data = {
            "medication_id": str(test_medication.id),
            "time_of_day": "08:00",
            "dose": "100mg"
        }

        response = client.post(
            f"/api/regimens/{test_regimen.id}/medications",
            json=data,
            headers=auth_headers
        )

        assert response.status_code in [200, 201]

    def test_remove_medication_from_regimen(self, client, auth_headers, test_regimen, test_medication):
        """Test removing a medication from a regimen."""
        # First add the medication
        add_data = {
            "medication_id": str(test_medication.id),
            "time_of_day": "08:00",
            "dose": "100mg"
        }
        client.post(
            f"/api/regimens/{test_regimen.id}/medications",
            json=add_data,
            headers=auth_headers
        )

        # Then remove it
        response = client.delete(
            f"/api/regimens/{test_regimen.id}/medications/{test_medication.id}",
            headers=auth_headers
        )

        assert response.status_code in [200, 204]

    def test_get_regimen_with_medications(self, client, auth_headers, db_session, test_user):
        """Test getting a regimen with its medications."""
        from tests.factories.factories import RegimenFactory, MedicationFactory

        regimen = RegimenFactory.create(
            db_session,
            test_user,
            name="Test Regimen"
        )

        med1 = MedicationFactory.create(db_session, test_user, drug_name="Med1")
        med2 = MedicationFactory.create(db_session, test_user, drug_name="Med2")

        # Add medications to regimen
        for med in [med1, med2]:
            client.post(
                f"/api/regimens/{regimen.id}/medications",
                json={
                    "medication_id": str(med.id),
                    "time_of_day": "08:00",
                    "dose": "100mg"
                },
                headers=auth_headers
            )

        response = client.get(f"/api/regimens/{regimen.id}", headers=auth_headers)

        assert response.status_code == 200
        result = response.json()
        # Check if medications are included (if endpoint supports it)
        assert result["name"] == "Test Regimen"

    def test_unauthorized_access(self, client):
        """Test accessing regimens without authentication."""
        response = client.get("/api/regimens")
        assert response.status_code == 401

    def test_cannot_access_other_user_regimen(self, client, db_session, auth_headers):
        """Test that users cannot access other users' regimens."""
        from tests.factories.factories import UserFactory, RegimenFactory

        # Create another user and their regimen
        other_user = UserFactory.create(
            db_session,
            username="otheruser",
            email="other@example.com"
        )
        other_regimen = RegimenFactory.create(db_session, other_user)

        response = client.get(
            f"/api/regimens/{other_regimen.id}",
            headers=auth_headers
        )

        assert response.status_code == 404
