from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID


class SymptomBase(BaseModel):
    """Base schema for symptom tracking data."""
    medication_id: UUID
    symptom_name: str = Field(..., min_length=1, max_length=200)
    improvement_level: int = Field(..., ge=1, le=10, description="Improvement level on scale 1-10")
    notes: Optional[str] = Field(None, max_length=2000)
    recorded_at: datetime

    @field_validator('improvement_level')
    @classmethod
    def validate_improvement_level(cls, v):
        if not 1 <= v <= 10:
            raise ValueError('improvement_level must be between 1 and 10')
        return v


class SymptomCreate(SymptomBase):
    """Schema for creating a symptom tracking entry."""
    pass


class SymptomUpdate(BaseModel):
    """Schema for updating a symptom tracking entry."""
    symptom_name: Optional[str] = Field(None, min_length=1, max_length=200)
    improvement_level: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = Field(None, max_length=2000)
    recorded_at: Optional[datetime] = None

    @field_validator('improvement_level')
    @classmethod
    def validate_improvement_level(cls, v):
        if v is not None and not 1 <= v <= 10:
            raise ValueError('improvement_level must be between 1 and 10')
        return v


class SymptomResponse(SymptomBase):
    """Schema for symptom tracking response."""
    id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class SymptomWithMedication(SymptomResponse):
    """Schema for symptom tracking with medication details."""
    medication: Optional[dict] = None

    class Config:
        from_attributes = True


class SymptomTrendData(BaseModel):
    """Schema for symptom trend analytics."""
    symptom_name: str
    medication_id: UUID
    medication_name: str
    average_improvement: float
    data_points: int
    trend: str  # "improving", "stable", "worsening"
    entries: list[dict]

    class Config:
        from_attributes = True
