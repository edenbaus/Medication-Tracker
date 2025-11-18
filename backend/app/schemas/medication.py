from datetime import date, datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from app.models.medication import PrescriptionType


class TagBasic(BaseModel):
    """Basic tag information for nested responses."""
    id: UUID
    name: str
    color: Optional[str] = None

    class Config:
        from_attributes = True


class ThirdPartyBasic(BaseModel):
    """Basic third party information for nested responses."""
    id: UUID
    name: str
    relationship_type: Optional[str] = None

    class Config:
        from_attributes = True


class MedicationBase(BaseModel):
    """Base medication schema with common fields."""
    drug_name: str = Field(..., min_length=1, max_length=255)
    pharmacy: Optional[str] = Field(None, max_length=255)
    prescription_type: PrescriptionType = PrescriptionType.LONG_TERM
    dosing_schedule: Optional[dict] = None
    standard_dose: str = Field(..., min_length=1, max_length=100)
    date_prescribed: Optional[date] = None
    date_filled: Optional[date] = None
    prescribing_doctor: Optional[str] = Field(None, max_length=255)
    prescription_number: Optional[str] = Field(None, max_length=100)
    quantity: Optional[int] = Field(None, ge=0, description="Number of pills/doses in prescription")
    refills_total: Optional[int] = Field(None, ge=0, description="Total refills authorized")
    refills_used: int = Field(0, ge=0, description="Number of refills used")
    days_supply: Optional[int] = Field(None, ge=1, le=365, description="Days supply per fill (e.g., 30, 90)")
    notes: Optional[str] = None
    active: bool = True
    start_date: date
    end_date: Optional[date] = None
    third_party_id: Optional[UUID] = None

    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v, info):
        """Validate that end_date is after start_date."""
        if v is not None and 'start_date' in info.data:
            if v < info.data['start_date']:
                raise ValueError('end_date must be after start_date')
        return v


class MedicationCreate(MedicationBase):
    """Schema for creating a new medication."""
    tag_ids: Optional[List[UUID]] = Field(default_factory=list)


class MedicationUpdate(BaseModel):
    """Schema for updating an existing medication."""
    drug_name: Optional[str] = Field(None, min_length=1, max_length=255)
    pharmacy: Optional[str] = Field(None, max_length=255)
    prescription_type: Optional[PrescriptionType] = None
    dosing_schedule: Optional[dict] = None
    standard_dose: Optional[str] = Field(None, min_length=1, max_length=100)
    date_prescribed: Optional[date] = None
    date_filled: Optional[date] = None
    prescribing_doctor: Optional[str] = Field(None, max_length=255)
    prescription_number: Optional[str] = Field(None, max_length=100)
    quantity: Optional[int] = Field(None, ge=0)
    refills_total: Optional[int] = Field(None, ge=0)
    refills_used: Optional[int] = Field(None, ge=0)
    days_supply: Optional[int] = Field(None, ge=1, le=365)
    notes: Optional[str] = None
    active: Optional[bool] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class MedicationResponse(MedicationBase):
    """Schema for medication responses."""
    id: UUID
    user_id: UUID
    third_party: Optional[ThirdPartyBasic] = None
    tags: List[TagBasic] = []
    created_at: datetime
    updated_at: datetime

    # Computed fields for refill tracking
    refills_remaining: Optional[int] = None
    is_due_for_refill: bool = False
    days_until_refill: Optional[int] = None
    refill_date: Optional[date] = None

    class Config:
        from_attributes = True


class MedicationList(BaseModel):
    """Schema for paginated medication list responses."""
    medications: List[MedicationResponse]
    total: int
    page: int = 1
    page_size: int = 50
