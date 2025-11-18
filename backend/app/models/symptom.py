import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class SymptomTracking(Base):
    """
    Symptom tracking model for monitoring symptom improvements.

    Records symptoms and their improvement levels on a 1-10 scale.
    """
    __tablename__ = "symptom_tracking"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    medication_id = Column(UUID(as_uuid=True), ForeignKey("medications.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    symptom_name = Column(String, nullable=False)
    improvement_level = Column(Integer, nullable=False)  # Scale 1-10
    notes = Column(Text, nullable=True)
    recorded_at = Column(DateTime, nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="symptom_trackings")
    medication = relationship("Medication", back_populates="symptoms")

    def __repr__(self):
        return f"<SymptomTracking(id={self.id}, symptom_name='{self.symptom_name}', improvement_level={self.improvement_level})>"
