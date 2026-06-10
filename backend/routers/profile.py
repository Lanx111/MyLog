"""Profile API routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import ProfileUpdate, ApiResponse
from crud import get_profile, upsert_profile

router = APIRouter(prefix="/api", tags=["profile"])


@router.get("/profile")
def read_profile(db: Session = Depends(get_db)):
    """Get personal profile info."""
    profile = get_profile(db)
    if not profile:
        return ApiResponse(code=404, message="Profile not found", data=None)
    return ApiResponse(data=profile.to_dict())


@router.put("/profile")
def update_profile(body: ProfileUpdate, db: Session = Depends(get_db)):
    """Update personal profile info. Only provided fields are updated."""
    data = body.model_dump(exclude_unset=True)
    profile = upsert_profile(db, data)
    return ApiResponse(data=profile.to_dict(), message="Profile updated")
