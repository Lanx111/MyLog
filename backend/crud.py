"""CRUD operations for database models."""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from models import Profile, Post


# ── Profile ──

def get_profile(db: Session) -> Profile | None:
    """Get the profile (single row with id=1)."""
    return db.query(Profile).filter(Profile.id == 1).first()


def upsert_profile(db: Session, data: dict) -> Profile:
    """Create or update the profile row."""
    profile = db.query(Profile).filter(Profile.id == 1).first()
    if not profile:
        profile = Profile(id=1)
        db.add(profile)

    for key, value in data.items():
        if value is not None:
            if key == "skills":
                profile.skills_list = value
            else:
                setattr(profile, key, value)

    profile.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(profile)
    return profile


# ── Posts ──

def get_posts(
    db: Session,
    post_type: str | None = None,
    page: int = 1,
    limit: int = 10,
    q: str | None = None,
) -> tuple[list[Post], int]:
    """Get paginated posts, optionally filtered by type and search keyword."""
    query = db.query(Post)

    if post_type:
        query = query.filter(Post.post_type == post_type)

    if q:
        keyword = f"%{q}%"
        query = query.filter(
            (Post.title.like(keyword)) | (Post.content.like(keyword))
        )

    total = query.count()
    posts = (
        query.order_by(Post.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return posts, total


def get_post(db: Session, post_id: int) -> Post | None:
    """Get a single post by id."""
    return db.query(Post).filter(Post.id == post_id).first()


def create_post(db: Session, data: dict) -> Post:
    """Create a new post."""
    post = Post(
        title=data["title"],
        content=data.get("content", ""),
        post_type=data.get("post_type", "work_log"),
    )
    if data.get("tags"):
        post.tags_list = data["tags"]

    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def update_post(db: Session, post_id: int, data: dict) -> Post | None:
    """Update an existing post."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        return None

    for key, value in data.items():
        if value is not None:
            if key == "tags":
                post.tags_list = value
            else:
                setattr(post, key, value)

    post.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, post_id: int) -> bool:
    """Delete a post. Returns True if deleted, False if not found."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        return False
    db.delete(post)
    db.commit()
    return True
