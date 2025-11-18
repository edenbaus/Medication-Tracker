"""File upload utilities for handling image uploads."""
import os
import uuid
from pathlib import Path
from typing import List
from fastapi import UploadFile, HTTPException


# Allowed image extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".heif"}

# Maximum file size (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

# Upload directory
UPLOAD_DIR = Path("/app/uploads")


def ensure_upload_directory():
    """Ensure the upload directory exists."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def validate_image_file(file: UploadFile) -> None:
    """
    Validate that the uploaded file is an allowed image type.

    Args:
        file: The uploaded file

    Raises:
        HTTPException: If the file is invalid
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Check content type
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )


async def save_upload_file(file: UploadFile, symptom_id: uuid.UUID) -> dict:
    """
    Save an uploaded file to disk.

    Args:
        file: The uploaded file
        symptom_id: The symptom ID to associate with

    Returns:
        dict: Information about the saved file

    Raises:
        HTTPException: If there's an error saving the file
    """
    # Validate the file
    validate_image_file(file)

    # Ensure upload directory exists
    ensure_upload_directory()

    # Create subdirectory for this symptom
    symptom_dir = UPLOAD_DIR / str(symptom_id)
    symptom_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    file_ext = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = symptom_dir / unique_filename

    # Read and save file
    try:
        contents = await file.read()

        # Check file size
        file_size = len(contents)
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
            )

        with open(file_path, "wb") as f:
            f.write(contents)

        return {
            "filename": file.filename,
            "file_path": str(file_path),
            "file_size": str(file_size),
            "content_type": file.content_type or "image/unknown"
        }
    except Exception as e:
        # Clean up if there was an error
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=500,
            detail=f"Error saving file: {str(e)}"
        )
    finally:
        await file.seek(0)


async def save_multiple_files(files: List[UploadFile], symptom_id: uuid.UUID) -> List[dict]:
    """
    Save multiple uploaded files.

    Args:
        files: List of uploaded files
        symptom_id: The symptom ID to associate with

    Returns:
        List[dict]: Information about all saved files
    """
    saved_files = []

    for file in files:
        try:
            file_info = await save_upload_file(file, symptom_id)
            saved_files.append(file_info)
        except HTTPException:
            # Clean up already saved files if one fails
            for saved_file in saved_files:
                file_path = Path(saved_file["file_path"])
                if file_path.exists():
                    file_path.unlink()
            raise

    return saved_files


def delete_symptom_images(symptom_id: uuid.UUID) -> None:
    """
    Delete all images for a symptom.

    Args:
        symptom_id: The symptom ID
    """
    symptom_dir = UPLOAD_DIR / str(symptom_id)
    if symptom_dir.exists():
        # Delete all files in the directory
        for file_path in symptom_dir.iterdir():
            if file_path.is_file():
                file_path.unlink()
        # Remove the directory
        symptom_dir.rmdir()


def delete_image_file(file_path: str) -> None:
    """
    Delete a specific image file.

    Args:
        file_path: Path to the file
    """
    path = Path(file_path)
    if path.exists() and path.is_file():
        path.unlink()

        # Try to remove parent directory if empty
        try:
            path.parent.rmdir()
        except OSError:
            # Directory not empty, that's fine
            pass
