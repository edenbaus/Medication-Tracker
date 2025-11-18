import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class SymptomImage(Base):
    """
    Symptom image model for storing images associated with symptom tracking entries.

    Supports multiple images per symptom tracking entry.
    """
    __tablename__ = "symptom_images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    symptom_id = Column(UUID(as_uuid=True), ForeignKey("symptom_tracking.id", ondelete="CASCADE"), nullable=False, index=True)

    # File information
    filename = Column(String, nullable=False)  # Original filename
    file_path = Column(String, nullable=False)  # Path to stored file
    file_size = Column(String, nullable=True)  # File size in bytes (stored as string)
    content_type = Column(String, nullable=True)  # MIME type

    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    symptom = relationship("SymptomTracking", back_populates="images")

    def __repr__(self):
        return f"<SymptomImage(id={self.id}, filename='{self.filename}')>"
