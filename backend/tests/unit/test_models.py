import pytest
from datetime import date, datetime, timedelta
from app.models import User, Medication, Tag, PrescriptionType, SeverityLevel


class TestMedicationModel:
    """Test suite for Medication model."""

    def test_medication_creation(self, db_session, test_user):
        """Test creating a medication."""
        medication = Medication(
            user_id=test_user.id,
            drug_name="Aspirin",
            standard_dose="100mg",
            prescription_type=PrescriptionType.OTC,
            start_date=date.today()
        )
        db_session.add(medication)
        db_session.commit()

        assert medication.id is not None
        assert medication.drug_name == "Aspirin"
        assert medication.standard_dose == "100mg"
        assert medication.prescription_type == PrescriptionType.OTC
        assert medication.active is True
        assert medication.user_id == test_user.id

    def test_medication_with_dosing_schedule(self, db_session, test_user):
        """Test medication with JSONB dosing schedule."""
        dosing_schedule = {
            "frequency": "daily",
            "times": ["08:00", "20:00"],
            "with_food": True
        }

        medication = Medication(
            user_id=test_user.id,
            drug_name="Lisinopril",
            standard_dose="10mg",
            dosing_schedule=dosing_schedule,
            prescription_type=PrescriptionType.LONG_TERM,
            start_date=date.today()
        )
        db_session.add(medication)
        db_session.commit()

        assert medication.dosing_schedule == dosing_schedule
        assert medication.dosing_schedule["frequency"] == "daily"
        assert len(medication.dosing_schedule["times"]) == 2

    def test_medication_with_end_date(self, db_session, test_user):
        """Test short-term medication with end date."""
        start = date.today()
        end = start + timedelta(days=10)

        medication = Medication(
            user_id=test_user.id,
            drug_name="Amoxicillin",
            standard_dose="500mg",
            prescription_type=PrescriptionType.SHORT_TERM,
            start_date=start,
            end_date=end
        )
        db_session.add(medication)
        db_session.commit()

        assert medication.end_date == end
        assert medication.end_date > medication.start_date

    def test_medication_user_relationship(self, db_session, test_user):
        """Test medication relationship with user."""
        medication = Medication(
            user_id=test_user.id,
            drug_name="Metformin",
            standard_dose="500mg",
            start_date=date.today()
        )
        db_session.add(medication)
        db_session.commit()

        assert medication.user == test_user
        assert medication in test_user.medications

    def test_medication_soft_delete(self, db_session, test_user):
        """Test soft deleting a medication by setting active=False."""
        medication = Medication(
            user_id=test_user.id,
            drug_name="Ibuprofen",
            standard_dose="200mg",
            start_date=date.today(),
            active=True
        )
        db_session.add(medication)
        db_session.commit()

        # Soft delete
        medication.active = False
        db_session.commit()

        assert medication.active is False
        assert medication.id is not None  # Still exists in database


class TestTagModel:
    """Test suite for Tag model."""

    def test_tag_creation(self, db_session, test_user):
        """Test creating a tag."""
        tag = Tag(
            user_id=test_user.id,
            name="Morning",
            color="#FF5733"
        )
        db_session.add(tag)
        db_session.commit()

        assert tag.id is not None
        assert tag.name == "Morning"
        assert tag.color == "#FF5733"
        assert tag.user_id == test_user.id

    def test_tag_without_color(self, db_session, test_user):
        """Test creating a tag without color."""
        tag = Tag(
            user_id=test_user.id,
            name="As Needed"
        )
        db_session.add(tag)
        db_session.commit()

        assert tag.id is not None
        assert tag.name == "As Needed"
        assert tag.color is None

    def test_tag_user_relationship(self, db_session, test_user):
        """Test tag relationship with user."""
        tag = Tag(
            user_id=test_user.id,
            name="Heart Health"
        )
        db_session.add(tag)
        db_session.commit()

        assert tag.user == test_user
        assert tag in test_user.tags

    def test_tag_unique_name_per_user(self, db_session, test_user):
        """Test that tag names must be unique per user."""
        tag1 = Tag(
            user_id=test_user.id,
            name="Daily"
        )
        db_session.add(tag1)
        db_session.commit()

        # Try to create duplicate tag
        tag2 = Tag(
            user_id=test_user.id,
            name="Daily"
        )
        db_session.add(tag2)

        with pytest.raises(Exception):  # Should raise IntegrityError
            db_session.commit()


class TestMedicationTagRelationship:
    """Test suite for medication-tag many-to-many relationship."""

    def test_medication_can_have_multiple_tags(self, db_session, test_user):
        """Test that a medication can have multiple tags."""
        medication = Medication(
            user_id=test_user.id,
            drug_name="Atorvastatin",
            standard_dose="20mg",
            start_date=date.today()
        )
        tag1 = Tag(user_id=test_user.id, name="Morning", color="#FF5733")
        tag2 = Tag(user_id=test_user.id, name="Heart Health", color="#33C3FF")

        medication.tags.extend([tag1, tag2])
        db_session.add(medication)
        db_session.commit()

        assert len(medication.tags) == 2
        assert tag1 in medication.tags
        assert tag2 in medication.tags

    def test_tag_can_have_multiple_medications(self, db_session, test_user):
        """Test that a tag can be associated with multiple medications."""
        tag = Tag(user_id=test_user.id, name="Daily", color="#00FF00")

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

        med1.tags.append(tag)
        med2.tags.append(tag)
        db_session.add_all([med1, med2])
        db_session.commit()

        assert len(tag.medications) == 2
        assert med1 in tag.medications
        assert med2 in tag.medications

    def test_tag_deletion_removes_associations(self, db_session, test_user):
        """Test that deleting a tag removes it from medications (CASCADE)."""
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

        tag_id = tag.id
        medication_id = medication.id

        # Delete tag
        db_session.delete(tag)
        db_session.commit()

        # Refresh medication
        db_session.expire(medication)
        medication = db_session.query(Medication).filter_by(id=medication_id).first()

        assert len(medication.tags) == 0

    def test_medication_deletion_removes_tag_associations(self, db_session, test_user):
        """Test that deleting a medication removes tag associations."""
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

        medication_id = medication.id
        tag_id = tag.id

        # Delete medication
        db_session.delete(medication)
        db_session.commit()

        # Tag should still exist but have no medications
        tag = db_session.query(Tag).filter_by(id=tag_id).first()
        assert tag is not None
        assert len(tag.medications) == 0

    def test_user_deletion_cascades_to_medications_and_tags(self, db_session):
        """Test that deleting a user cascades to medications and tags."""
        user = User(
            username="testuser2",
            email="test2@example.com",
            password_hash="hashed"
        )
        db_session.add(user)
        db_session.commit()

        medication = Medication(
            user_id=user.id,
            drug_name="Test Med",
            standard_dose="10mg",
            start_date=date.today()
        )
        tag = Tag(user_id=user.id, name="Test Tag")
        medication.tags.append(tag)
        db_session.add(medication)
        db_session.commit()

        medication_id = medication.id
        tag_id = tag.id
        user_id = user.id

        # Delete user
        db_session.delete(user)
        db_session.commit()

        # Medications and tags should be deleted
        assert db_session.query(Medication).filter_by(id=medication_id).first() is None
        assert db_session.query(Tag).filter_by(id=tag_id).first() is None
