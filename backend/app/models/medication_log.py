import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class MedicationLog(Base):
    """
    Medication log model for tracking medication intake.

    Records when medications are taken, dose taken, and optional notes.
    """
    __tablename__ = "medication_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    medication_id = Column(UUID(as_uuid=True), ForeignKey("medications.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    taken_at = Column(DateTime, nullable=False, index=True)
    dose_taken = Column(String, nullable=False)
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="medication_logs")
    medication = relationship("Medication", back_populates="logs")

    def __repr__(self):
        return f"<MedicationLog(id={self.id}, medication_id={self.medication_id}, taken_at={self.taken_at})>"
