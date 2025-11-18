"""Test data factories for creating test objects."""
from datetime import date, datetime, timedelta
from typing import Optional
from uuid import UUID
from app.models.user import User
from app.models.medication import Medication, PrescriptionType
from app.models.medication_log import MedicationLog
from app.models.side_effect import SideEffect
from app.models.symptom import SymptomTracking
from app.models.tag import Tag
from app.models.third_party import ThirdParty
from app.models.regimen import Regimen
from app.utils.security import get_password_hash


class UserFactory:
    """Factory for creating User objects."""

    @staticmethod
    def create(
        db,
        username: str = "testuser",
        email: str = "test@example.com",
        password: str = "testpassword123",
        is_admin: bool = False,
        **kwargs
    ) -> User:
        """Create a user."""
        user = User(
            username=username,
            email=email,
            password_hash=get_password_hash(password),
            is_admin=is_admin,
            **kwargs
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


class ThirdPartyFactory:
    """Factory for creating ThirdParty objects."""

    @staticmethod
    def create(
        db,
        user: User,
        name: str = "Family Member",
        relationship_type: str = "child",
        **kwargs
    ) -> ThirdParty:
        """Create a third party."""
        third_party = ThirdParty(
            user_id=user.id,
            name=name,
            relationship_type=relationship_type,
            **kwargs
        )
        db.add(third_party)
        db.commit()
        db.refresh(third_party)
        return third_party


class TagFactory:
    """Factory for creating Tag objects."""

    @staticmethod
    def create(
        db,
        user: User,
        name: str = "Test Tag",
        color: str = "#FF5733",
        **kwargs
    ) -> Tag:
        """Create a tag."""
        tag = Tag(
            user_id=user.id,
            name=name,
            color=color,
            **kwargs
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)
        return tag


class MedicationFactory:
    """Factory for creating Medication objects."""

    @staticmethod
    def create(
        db,
        user: User,
        drug_name: str = "Test Medication",
        standard_dose: str = "100mg",
        prescription_type: PrescriptionType = PrescriptionType.LONG_TERM,
        start_date: Optional[date] = None,
        active: bool = True,
        third_party: Optional[ThirdParty] = None,
        **kwargs
    ) -> Medication:
        """Create a medication."""
        if start_date is None:
            start_date = date.today()

        medication = Medication(
            user_id=user.id,
            drug_name=drug_name,
            standard_dose=standard_dose,
            prescription_type=prescription_type,
            start_date=start_date,
            active=active,
            third_party_id=third_party.id if third_party else None,
            **kwargs
        )
        db.add(medication)
        db.commit()
        db.refresh(medication)
        return medication


class MedicationLogFactory:
    """Factory for creating MedicationLog objects."""

    @staticmethod
    def create(
        db,
        medication: Medication,
        dose_taken: str = "100mg",
        taken_at: Optional[datetime] = None,
        **kwargs
    ) -> MedicationLog:
        """Create a medication log."""
        if taken_at is None:
            taken_at = datetime.utcnow()

        log = MedicationLog(
            medication_id=medication.id,
            user_id=medication.user_id,  # Get user_id from medication
            dose_taken=dose_taken,
            taken_at=taken_at,
            **kwargs
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log


class SideEffectFactory:
    """Factory for creating SideEffect objects."""

    @staticmethod
    def create(
        db,
        user: User,
        medication: Medication,
        description: str = "Test side effect",
        severity: str = "mild",
        occurred_at: Optional[datetime] = None,
        **kwargs
    ) -> SideEffect:
        """Create a side effect."""
        if occurred_at is None:
            occurred_at = datetime.utcnow()

        side_effect = SideEffect(
            user_id=user.id,
            medication_id=medication.id,
            description=description,
            severity=severity,
            occurred_at=occurred_at,
            **kwargs
        )
        db.add(side_effect)
        db.commit()
        db.refresh(side_effect)
        return side_effect


class SymptomFactory:
    """Factory for creating SymptomTracking objects."""

    @staticmethod
    def create(
        db,
        user: User,
        medication: Medication,
        symptom_name: str = "Test symptom",
        improvement_level: int = 5,
        recorded_at: Optional[datetime] = None,
        **kwargs
    ) -> SymptomTracking:
        """Create a symptom tracking entry."""
        if recorded_at is None:
            recorded_at = datetime.utcnow()

        symptom = SymptomTracking(
            user_id=user.id,
            medication_id=medication.id,
            symptom_name=symptom_name,
            improvement_level=improvement_level,
            recorded_at=recorded_at,
            **kwargs
        )
        db.add(symptom)
        db.commit()
        db.refresh(symptom)
        return symptom


class RegimenFactory:
    """Factory for creating Regimen objects."""

    @staticmethod
    def create(
        db,
        user: User,
        name: str = "Morning Regimen",
        description: str = "Morning medication schedule",
        **kwargs
    ) -> Regimen:
        """Create a regimen."""
        regimen = Regimen(
            user_id=user.id,
            name=name,
            description=description,
            **kwargs
        )
        db.add(regimen)
        db.commit()
        db.refresh(regimen)
        return regimen
