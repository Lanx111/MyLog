"""Posts API routes."""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas import PostCreate, PostUpdate, ApiResponse, PaginatedData
from crud import get_posts, get_post, create_post, update_post, delete_post
from dependencies import get_current_user, get_optional_user
from models import User

router = APIRouter(prefix="/api", tags=["posts"])


@router.get("/posts")
def list_posts(
    post_type: str | None = Query(None),
    user_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    q: str | None = Query(None),
    db: Session = Depends(get_db),
):
    """Get paginated posts (public). Supports filter by type, user, and search."""
    posts, total = get_posts(db, post_type=post_type, user_id=user_id, page=page, limit=limit, q=q)
    return ApiResponse(
        data=PaginatedData(
            items=[p.to_dict() for p in posts],
            total=total,
            page=page,
            limit=limit,
        )
    )


@router.get("/posts/{post_id}")
def read_post(post_id: int, db: Session = Depends(get_db)):
    """Get a single post by id (public)."""
    post = get_post(db, post_id)
    if not post:
        return ApiResponse(code=404, message="Post not found", data=None)
    return ApiResponse(data=post.to_dict())


@router.post("/posts")
def create_new_post(
    body: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a post (auth required). Automatically owned by current user."""
    post = create_post(db, current_user.id, body.model_dump())
    return ApiResponse(data=post.to_dict(), message="Post created")


@router.put("/posts/{post_id}")
def edit_post(
    post_id: int,
    body: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a post (only the author can edit)."""
    post = get_post(db, post_id)
    if not post:
        return ApiResponse(code=404, message="Post not found", data=None)
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权修改他人的日志")
    data = body.model_dump(exclude_unset=True)
    updated = update_post(db, post_id, data)
    return ApiResponse(data=updated.to_dict(), message="Post updated")


@router.delete("/posts/{post_id}")
def remove_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a post (only the author can delete)."""
    post = get_post(db, post_id)
    if not post:
        return ApiResponse(code=404, message="Post not found", data=None)
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除他人的日志")
    delete_post(db, post_id)
    return ApiResponse(message="Post deleted")
