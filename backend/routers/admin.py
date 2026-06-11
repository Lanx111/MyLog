"""Admin API routes — manage all users and posts."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas import ApiResponse
from models import User, Post, Profile
from dependencies import get_current_user, get_admin_user

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users")
def list_users(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """List all users with their profile info (admin only)."""
    users = db.query(User).all()
    result = []
    for u in users:
        profile = db.query(Profile).filter(Profile.user_id == u.id).first()
        post_count = db.query(Post).filter(Post.user_id == u.id).count()
        result.append({
            **u.to_dict(),
            "profile": profile.to_dict() if profile else None,
            "post_count": post_count,
        })
    return ApiResponse(data=result)


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Delete a user and all their data (admin only)."""
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="不能删除自己")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return ApiResponse(code=404, message="用户不存在")

    # Cascade: delete profile + posts, then delete user
    db.query(Post).filter(Post.user_id == user_id).delete()
    db.query(Profile).filter(Profile.user_id == user_id).delete()
    db.delete(user)
    db.commit()
    return ApiResponse(message=f"已删除用户 {user.username} 及其所有数据")


@router.delete("/posts/{post_id}")
def delete_any_post(
    post_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Delete any post regardless of owner (admin only)."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        return ApiResponse(code=404, message="日志不存在")
    db.delete(post)
    db.commit()
    return ApiResponse(message="日志已删除")
