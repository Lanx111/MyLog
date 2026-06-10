"""Posts API routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas import PostCreate, PostUpdate, ApiResponse, PaginatedData
from crud import get_posts, get_post, create_post, update_post, delete_post

router = APIRouter(prefix="/api", tags=["posts"])


@router.get("/posts")
def list_posts(
    post_type: str | None = Query(None, description="Filter by post type"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    q: str | None = Query(None, description="Search keyword"),
    db: Session = Depends(get_db),
):
    """Get paginated posts list with optional type filter and search."""
    posts, total = get_posts(db, post_type=post_type, page=page, limit=limit, q=q)
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
    """Get a single post by id."""
    post = get_post(db, post_id)
    if not post:
        return ApiResponse(code=404, message="Post not found", data=None)
    return ApiResponse(data=post.to_dict())


@router.post("/posts")
def create_new_post(body: PostCreate, db: Session = Depends(get_db)):
    """Create a new post."""
    post = create_post(db, body.model_dump())
    return ApiResponse(data=post.to_dict(), message="Post created")


@router.put("/posts/{post_id}")
def edit_post(post_id: int, body: PostUpdate, db: Session = Depends(get_db)):
    """Update an existing post. Only provided fields are updated."""
    data = body.model_dump(exclude_unset=True)
    post = update_post(db, post_id, data)
    if not post:
        return ApiResponse(code=404, message="Post not found", data=None)
    return ApiResponse(data=post.to_dict(), message="Post updated")


@router.delete("/posts/{post_id}")
def remove_post(post_id: int, db: Session = Depends(get_db)):
    """Delete a post."""
    ok = delete_post(db, post_id)
    if not ok:
        return ApiResponse(code=404, message="Post not found", data=None)
    return ApiResponse(message="Post deleted")
