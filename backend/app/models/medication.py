import uuid
import enum
from datetime import datetime, date, timedelta
from sqlalchemy import Column, String, Boolean, DateTime, Date, ForeignKey, Enum, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class PrescriptionType(str, enum.Enum):
    """Enum for prescription types."""
    LONG_TERM = "long_term"
    SHORT_TERM = "short_term"
    OTC = "otc"


class Medication(Base):
    """
    Medication model for tracking prescription and OTC medications.

    Supports long-term prescriptions, short-term medications, and OTC drugs.
    """
    __tablename__ = "medications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    third_party_id = Column(UUID(as_uuid=True), ForeignKey("third_parties.id", ondelete="SET NULL"), nullable=True, index=True)

    # Medication details
    drug_name = Column(String, nullable=False, index=True)
    pharmacy = Column(String, nullable=True)
    prescription_type = Column(Enum(PrescriptionType, values_callable=lambda obj: [e.value for e in obj]), nullable=False, default=PrescriptionType.LONG_TERM)

    # Dosing information
    dosing_schedule = Column(JSONB, nullable=True)  # Flexible structure for various schedules
    standard_dose = Column(String, nullable=False)  # e.g., "10mg", "2 tablets"

    # Prescription details
    date_prescribed = Column(Date, nullable=True)
    date_filled = Column(Date, nullable=True)
    prescribing_doctor = Column(String, nullable=True)
    prescription_number = Column(String, nullable=True)

    # Refill tracking
    quantity = Column(Integer, nullable=True)  # Number of pills/doses in prescription
    refills_total = Column(Integer, nullable=True)  # Total refills authorized
    refills_used = Column(Integer, default=0, nullable=False)  # Number of refills used
    days_supply = Column(Integer, nullable=True)  # Days supply per fill (e.g., 30, 90)

    # Additional information
    notes = Column(Text, nullable=True)
    active = Column(Boolean, default=True, nullable=False, index=True)
    start_date = Column(Date, nullable=False, default=date.today)
    end_date = Column(Date, nullable=True)  # For short-term medications

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="medications")
    third_party = relationship("ThirdParty", back_populates="medications")
    tags = relationship("Tag", secondary="medication_tags", back_populates="medications")
    logs = relationship("MedicationLog", back_populates="medication", cascade="all, delete-orphan")
    side_effects = relationship("SideEffect", back_populates="medication", cascade="all, delete-orphan")
    symptoms = relationship("SymptomTracking", back_populates="medication", cascade="all, delete-orphan")
    regimens = relationship("Regimen", secondary="regimen_medications", back_populates="medications")

    def __repr__(self):
        return f"<Medication(id={self.id}, drug_name='{self.drug_name}', user_id={self.user_id})>"

    @property
    def refills_remaining(self) -> int:
        """Calculate remaining refills."""
        if self.refills_total is None:
            return 0
        return max(0, self.refills_total - self.refills_used)

    @property
    def is_due_for_refill(self) -> bool:
        """Check if medication is due for refill based on days supply and last fill date."""
        if not self.date_filled or not self.days_supply:
            return False

        # Calculate expected next refill date
        next_refill_date = self.date_filled + timedelta(days=self.days_supply)

        # Consider due if within 7 days of next refill date
        today = date.today()
        days_until_refill = (next_refill_date - today).days

        return days_until_refill <= 7

    @property
    def days_until_refill(self) -> int:
        """Calculate days until refill is due."""
        if not self.date_filled or not self.days_supply:
            return 0

        next_refill_date = self.date_filled + timedelta(days=self.days_supply)
        today = date.today()
        days_until = (next_refill_date - today).days

        return max(0, days_until)

    @property
    def refill_date(self) -> date:
        """Calculate the expected refill date."""
        if not self.date_filled or not self.days_supply:
            return None

        return self.date_filled + timedelta(days=self.days_supply)
