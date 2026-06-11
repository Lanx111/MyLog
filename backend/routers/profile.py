"""Profile API routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import ProfileUpdate, ApiResponse
from crud import get_profile_by_user, get_all_profiles, upsert_profile
from dependencies import get_current_user
from models import User

router = APIRouter(prefix="/api", tags=["profile"])


@router.get("/profiles")
def list_profiles(db: Session = Depends(get_db)):
    """Get all user profiles (public, no auth required)."""
    profiles = get_all_profiles(db)
    return ApiResponse(data=[p.to_dict() for p in profiles])


@router.get("/profile")
def read_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the current user's own profile."""
    profile = get_profile_by_user(db, current_user.id)
    if not profile:
        return ApiResponse(code=404, message="Profile not found", data=None)
    return ApiResponse(data=profile.to_dict())


@router.put("/profile")
def update_profile(
    body: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update current user's own profile."""
    data = body.model_dump(exclude_unset=True)
    profile = upsert_profile(db, current_user.id, data)
    return ApiResponse(data=profile.to_dict(), message="Profile updated")
