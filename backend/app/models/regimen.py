import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


# Junction table for regimen-medication many-to-many relationship
regimen_medications = Table(
    'regimen_medications',
    Base.metadata,
    Column('regimen_id', UUID(as_uuid=True), ForeignKey('regimens.id', ondelete='CASCADE'), primary_key=True),
    Column('medication_id', UUID(as_uuid=True), ForeignKey('medications.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', String, default=lambda: datetime.utcnow().isoformat())
)


class Regimen(Base):
    """
    Regimen model for grouping medications together.

    A regimen is a group of medications taken together at specific times
    (e.g., "Morning Routine", "Bedtime Meds", "Diabetes Management").
    """
    __tablename__ = "regimens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Regimen information
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True)  # Hex color code for UI display

    # Timestamps
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())

    # Relationships
    user = relationship("User", back_populates="regimens")
    medications = relationship(
        "Medication",
        secondary=regimen_medications,
        back_populates="regimens"
    )

    def __repr__(self):
        return f"<Regimen(id={self.id}, name={self.name}, user_id={self.user_id})>"
