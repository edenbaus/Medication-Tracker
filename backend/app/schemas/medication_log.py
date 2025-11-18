from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from uuid import UUID
from typing import Optional


class MedicationLogBase(BaseModel):
    """Base medication log schema with common attributes."""
    medication_id: UUID
    dose_taken: str = Field(..., min_length=1, max_length=100, description="Dose taken, e.g., '10mg', '2 tablets'")
    notes: Optional[str] = Field(None, max_length=1000)

    @field_validator('dose_taken')
    @classmethod
    def validate_dose(cls, v):
        """Validate dose format."""
        if v and v.strip() != v:
            raise ValueError('dose_taken cannot have leading/trailing whitespace')
        if not v or not v.strip():
            raise ValueError('dose_taken cannot be empty')
        return v.strip()


class MedicationLogCreate(MedicationLogBase):
    """Schema for creating a medication log entry."""
    taken_at: Optional[datetime] = Field(None, description="When medication was taken (defaults to now)")

    @field_validator('taken_at')
    @classmethod
    def validate_taken_at(cls, v):
        """Validate that taken_at is not in the future."""
        if v and v > datetime.utcnow():
            raise ValueError('taken_at cannot be in the future')
        return v


class MedicationLogUpdate(BaseModel):
    """Schema for updating a medication log entry."""
    dose_taken: Optional[str] = Field(None, min_length=1, max_length=100)
    taken_at: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=1000)

    @field_validator('dose_taken')
    @classmethod
    def validate_dose(cls, v):
        """Validate dose format."""
        if v is not None:
            if v.strip() != v:
                raise ValueError('dose_taken cannot have leading/trailing whitespace')
            if not v.strip():
                raise ValueError('dose_taken cannot be empty')
            return v.strip()
        return v

    @field_validator('taken_at')
    @classmethod
    def validate_taken_at(cls, v):
        """Validate that taken_at is not in the future."""
        if v and v > datetime.utcnow():
            raise ValueError('taken_at cannot be in the future')
        return v


class MedicationLogResponse(MedicationLogBase):
    """Schema for medication log response."""
    id: UUID
    user_id: UUID
    taken_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MedicationLogWithMedication(MedicationLogResponse):
    """Schema for medication log with medication details."""
    medication_name: str = Field(..., alias="medication_drug_name")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class MedicationLogList(BaseModel):
    """Schema for paginated list of medication logs."""
    logs: list[MedicationLogResponse]
    total: int
    page: int = 1
    page_size: int = 50


class AdherenceStats(BaseModel):
    """Schema for adherence statistics."""
    medication_id: UUID
    medication_name: str
    total_expected_doses: int
    total_logged_doses: int
    adherence_percentage: float
    period_start: datetime
    period_end: datetime


class OverallAdherenceStats(BaseModel):
    """Schema for overall adherence statistics."""
    total_medications: int
    total_logged_doses: int
    average_adherence: float
    period_start: datetime
    period_end: datetime
    medication_stats: list[AdherenceStats]


class DailyUsageData(BaseModel):
    """Schema for daily usage data point."""
    date: str  # ISO format date string
    count: int
    medications: list[str]  # List of medication names taken that day


class PersonUsageData(BaseModel):
    """Schema for usage data grouped by person."""
    person_id: Optional[UUID] = None  # None means self
    person_name: str
    color: str  # Color for chart display
    daily_data: list[DailyUsageData]
    total_logs: int


class MedicationUsageTimeline(BaseModel):
    """Schema for medication usage over time."""
    medication_id: Optional[UUID] = None
    medication_name: Optional[str] = None
    period_start: datetime
    period_end: datetime
    total_logs: int
    daily_data: list[DailyUsageData]
    grouping: str  # "daily" or "weekly"
    by_person: list[PersonUsageData] = []  # Data grouped by person
