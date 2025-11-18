from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base


class User(Base):
    """User model for authentication and data ownership."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True)  # Nullable for OAuth users
    is_admin = Column(Boolean, default=False, nullable=False)

    # OAuth fields
    oauth_provider = Column(String, nullable=True)  # 'google', 'github', or None
    oauth_id = Column(String, nullable=True, index=True)  # User ID from OAuth provider

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    medications = relationship("Medication", back_populates="user", cascade="all, delete-orphan")
    tags = relationship("Tag", back_populates="user", cascade="all, delete-orphan")
    medication_logs = relationship("MedicationLog", back_populates="user", cascade="all, delete-orphan")
    side_effects = relationship("SideEffect", back_populates="user", cascade="all, delete-orphan")
    symptom_trackings = relationship("SymptomTracking", back_populates="user", cascade="all, delete-orphan")
    third_parties = relationship("ThirdParty", back_populates="user", cascade="all, delete-orphan")
    regimens = relationship("Regimen", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
