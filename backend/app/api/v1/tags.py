from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.database import get_db
from app.api.deps import get_current_user
from app.models import User, Tag, Medication, medication_tags
from app.schemas.tag import TagCreate, TagUpdate, TagResponse, TagList, TagWithMedicationCount

router = APIRouter()


@router.get("/", response_model=TagList)
def get_tags(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all tags for the current user.

    Returns tags ordered by creation date (newest first).
    """
    tags = db.query(Tag).filter(Tag.user_id == current_user.id).order_by(Tag.created_at.desc()).all()

    return TagList(tags=tags, total=len(tags))


@router.get("/with-counts", response_model=List[TagWithMedicationCount])
def get_tags_with_medication_counts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all tags with medication counts.

    Returns tags with the count of active medications associated with each tag.
    """
    # Query tags with medication counts
    tags_with_counts = db.query(
        Tag,
        func.count(Medication.id).label('medication_count')
    ).outerjoin(
        medication_tags, Tag.id == medication_tags.c.tag_id
    ).outerjoin(
        Medication,
        and_(
            medication_tags.c.medication_id == Medication.id,
            Medication.active == True
        )
    ).filter(
        Tag.user_id == current_user.id
    ).group_by(Tag.id).order_by(Tag.created_at.desc()).all()

    result = []
    for tag, count in tags_with_counts:
        tag_dict = {
            "id": tag.id,
            "user_id": tag.user_id,
            "name": tag.name,
            "color": tag.color,
            "created_at": tag.created_at,
            "updated_at": tag.updated_at,
            "medication_count": count or 0
        }
        result.append(TagWithMedicationCount(**tag_dict))

    return result


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(
    tag_in: TagCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new tag for the current user.

    Tag names must be unique per user.
    """
    # Check if tag name already exists for this user
    existing_tag = db.query(Tag).filter(
        and_(
            Tag.user_id == current_user.id,
            Tag.name == tag_in.name
        )
    ).first()

    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag with name '{tag_in.name}' already exists"
        )

    # Create tag
    tag = Tag(**tag_in.model_dump(), user_id=current_user.id)
    db.add(tag)
    db.commit()
    db.refresh(tag)

    return tag


@router.get("/{tag_id}", response_model=TagResponse)
def get_tag(
    tag_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific tag by ID.

    Only returns the tag if it belongs to the current user.
    """
    tag = db.query(Tag).filter(
        and_(
            Tag.id == tag_id,
            Tag.user_id == current_user.id
        )
    ).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    return tag


@router.put("/{tag_id}", response_model=TagResponse)
def update_tag(
    tag_id: UUID,
    tag_in: TagUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing tag.

    Only allows updating tags that belong to the current user.
    If renaming, the new name must still be unique for this user.
    """
    tag = db.query(Tag).filter(
        and_(
            Tag.id == tag_id,
            Tag.user_id == current_user.id
        )
    ).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    # If updating name, check for uniqueness
    if tag_in.name and tag_in.name != tag.name:
        existing_tag = db.query(Tag).filter(
            and_(
                Tag.user_id == current_user.id,
                Tag.name == tag_in.name,
                Tag.id != tag_id
            )
        ).first()

        if existing_tag:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tag with name '{tag_in.name}' already exists"
            )

    # Update tag fields
    update_data = tag_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tag, field, value)

    db.commit()
    db.refresh(tag)

    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    tag_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a tag.

    Only allows deleting tags that belong to the current user.
    This will also remove the tag from all medications (CASCADE).
    """
    tag = db.query(Tag).filter(
        and_(
            Tag.id == tag_id,
            Tag.user_id == current_user.id
        )
    ).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    db.delete(tag)
    db.commit()

    return None


@router.get("/{tag_id}/medications", response_model=List[UUID])
def get_tag_medications(
    tag_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all medications associated with a specific tag.

    Returns a list of medication IDs.
    """
    tag = db.query(Tag).filter(
        and_(
            Tag.id == tag_id,
            Tag.user_id == current_user.id
        )
    ).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    medication_ids = [med.id for med in tag.medications if med.active]

    return medication_ids
