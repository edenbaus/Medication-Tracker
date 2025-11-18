from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.third_party import ThirdParty
from app.models.user import User
from app.schemas.third_party import ThirdPartyCreate, ThirdPartyUpdate, ThirdPartyResponse
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=List[ThirdPartyResponse])
def get_third_parties(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all third parties for the current user.
    """
    third_parties = db.query(ThirdParty).filter(
        ThirdParty.user_id == current_user.id
    ).all()

    return third_parties


@router.get("/{third_party_id}", response_model=ThirdPartyResponse)
def get_third_party(
    third_party_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific third party by ID.
    """
    third_party = db.query(ThirdParty).filter(
        ThirdParty.id == third_party_id,
        ThirdParty.user_id == current_user.id
    ).first()

    if not third_party:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Third party not found"
        )

    return third_party


@router.post("/", response_model=ThirdPartyResponse, status_code=status.HTTP_201_CREATED)
def create_third_party(
    third_party_data: ThirdPartyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new third party.
    """
    # Create new third party
    new_third_party = ThirdParty(
        user_id=current_user.id,
        **third_party_data.model_dump()
    )

    db.add(new_third_party)
    db.commit()
    db.refresh(new_third_party)

    return new_third_party


@router.put("/{third_party_id}", response_model=ThirdPartyResponse)
def update_third_party(
    third_party_id: UUID,
    third_party_data: ThirdPartyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a third party.
    """
    third_party = db.query(ThirdParty).filter(
        ThirdParty.id == third_party_id,
        ThirdParty.user_id == current_user.id
    ).first()

    if not third_party:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Third party not found"
        )

    # Update fields
    update_data = third_party_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(third_party, field, value)

    db.commit()
    db.refresh(third_party)

    return third_party


@router.delete("/{third_party_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_third_party(
    third_party_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a third party.
    Note: This will set medications' third_party_id to NULL (not delete the medications).
    """
    third_party = db.query(ThirdParty).filter(
        ThirdParty.id == third_party_id,
        ThirdParty.user_id == current_user.id
    ).first()

    if not third_party:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Third party not found"
        )

    db.delete(third_party)
    db.commit()

    return None
