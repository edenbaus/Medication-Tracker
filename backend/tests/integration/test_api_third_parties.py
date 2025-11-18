"""Integration tests for Third Parties API endpoints."""
import pytest


class TestThirdPartiesAPI:
    """Test third parties API endpoints."""

    def test_create_third_party(self, client, auth_headers):
        """Test creating a third party."""
        data = {
            "name": "John Doe",
            "relationship_type": "spouse",
            "date_of_birth": "1980-01-15",
            "notes": "Primary caregiver"
        }

        response = client.post("/api/third-parties", json=data, headers=auth_headers)

        assert response.status_code == 201
        result = response.json()
        assert result["name"] == "John Doe"
        assert result["relationship_type"] == "spouse"

    def test_create_third_party_minimal(self, client, auth_headers):
        """Test creating third party with minimal data."""
        data = {
            "name": "Jane Doe",
            "relationship_type": "child"
        }

        response = client.post("/api/third-parties", json=data, headers=auth_headers)

        assert response.status_code == 201
        result = response.json()
        assert result["name"] == "Jane Doe"
        assert result["relationship_type"] == "child"

    def test_list_third_parties(self, client, auth_headers, test_third_party):
        """Test listing third parties."""
        response = client.get("/api/third-parties", headers=auth_headers)

        assert response.status_code == 200
        result = response.json()
        assert len(result) >= 1
        assert any(tp["id"] == str(test_third_party.id) for tp in result)

    def test_get_third_party(self, client, auth_headers, test_third_party):
        """Test getting a specific third party."""
        response = client.get(
            f"/api/third-parties/{test_third_party.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        result = response.json()
        assert result["id"] == str(test_third_party.id)
        assert result["name"] == test_third_party.name

    def test_get_third_party_not_found(self, client, auth_headers):
        """Test getting non-existent third party."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = client.get(f"/api/third-parties/{fake_id}", headers=auth_headers)

        assert response.status_code == 404

    def test_update_third_party(self, client, auth_headers, test_third_party):
        """Test updating a third party."""
        data = {
            "name": "Updated Name",
            "relationship_type": "parent",
            "notes": "Updated notes"
        }

        response = client.put(
            f"/api/third-parties/{test_third_party.id}",
            json=data,
            headers=auth_headers
        )

        assert response.status_code == 200
        result = response.json()
        assert result["name"] == "Updated Name"
        assert result["relationship_type"] == "parent"

    def test_delete_third_party(self, client, auth_headers, test_third_party):
        """Test deleting a third party."""
        response = client.delete(
            f"/api/third-parties/{test_third_party.id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verify deletion
        get_response = client.get(
            f"/api/third-parties/{test_third_party.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    def test_third_party_with_medications(self, client, auth_headers, db_session, test_user, test_third_party):
        """Test third party with associated medications."""
        from tests.factories.factories import MedicationFactory

        # Create medications for third party
        med1 = MedicationFactory.create(
            db_session,
            test_user,
            drug_name="Med for Child",
            third_party=test_third_party
        )

        response = client.get(
            f"/api/medications?third_party_id={test_third_party.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        result = response.json()
        assert len(result["medications"]) >= 1
        assert any(m["third_party_id"] == str(test_third_party.id) for m in result["medications"])

    def test_cannot_delete_third_party_with_medications(self, client, auth_headers, db_session, test_user, test_third_party):
        """Test that third party with medications cannot be deleted (if enforced)."""
        from tests.factories.factories import MedicationFactory

        # Create medication for third party
        MedicationFactory.create(
            db_session,
            test_user,
            third_party=test_third_party
        )

        response = client.delete(
            f"/api/third-parties/{test_third_party.id}",
            headers=auth_headers
        )

        # Depending on implementation, this could be 400, 409, or 204 with cascade delete
        assert response.status_code in [204, 400, 409]

    def test_filter_medications_by_third_party(self, client, auth_headers, db_session, test_user):
        """Test filtering medications by third party."""
        from tests.factories.factories import ThirdPartyFactory, MedicationFactory

        tp1 = ThirdPartyFactory.create(db_session, test_user, name="Person 1")
        tp2 = ThirdPartyFactory.create(db_session, test_user, name="Person 2")

        med1 = MedicationFactory.create(db_session, test_user, drug_name="Med1", third_party=tp1)
        med2 = MedicationFactory.create(db_session, test_user, drug_name="Med2", third_party=tp2)

        response = client.get(
            f"/api/medications?third_party_id={tp1.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        result = response.json()
        assert all(m["third_party_id"] == str(tp1.id) for m in result["medications"])

    def test_dashboard_shows_third_party_stats(self, client, auth_headers, db_session, test_user, test_third_party):
        """Test that dashboard includes third party statistics."""
        from tests.factories.factories import MedicationFactory, MedicationLogFactory

        # Create medication and log for third party
        med = MedicationFactory.create(
            db_session,
            test_user,
            drug_name="Child Med",
            third_party=test_third_party
        )
        MedicationLogFactory.create(db_session, med)

        response = client.get("/api/dashboard/summary", headers=auth_headers)

        assert response.status_code == 200
        result = response.json()
        assert "people_stats" in result
        # Check that third party stats are included
        assert any(
            p["person_name"] == test_third_party.name
            for p in result["people_stats"]
        )

    def test_unauthorized_access(self, client):
        """Test accessing third parties without authentication."""
        response = client.get("/api/third-parties")
        assert response.status_code == 401

    def test_cannot_access_other_user_third_party(self, client, db_session, auth_headers):
        """Test that users cannot access other users' third parties."""
        from tests.factories.factories import UserFactory, ThirdPartyFactory

        # Create another user and their third party
        other_user = UserFactory.create(
            db_session,
            username="otheruser",
            email="other@example.com"
        )
        other_tp = ThirdPartyFactory.create(db_session, other_user)

        response = client.get(
            f"/api/third-parties/{other_tp.id}",
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_create_multiple_third_parties(self, client, auth_headers):
        """Test creating multiple third parties."""
        relationships = [
            ("Child 1", "child"),
            ("Child 2", "child"),
            ("Parent", "parent"),
            ("Spouse", "spouse")
        ]

        for name, rel_type in relationships:
            data = {
                "name": name,
                "relationship_type": rel_type
            }
            response = client.post("/api/third-parties", json=data, headers=auth_headers)
            assert response.status_code == 201

        # Verify all created
        response = client.get("/api/third-parties", headers=auth_headers)
        assert response.status_code == 200
        result = response.json()
        assert len(result) >= len(relationships)
