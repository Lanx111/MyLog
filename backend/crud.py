"""CRUD operations for database models."""
from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload

from models import User, Profile, Post
from auth_utils import hash_password


# ── Users ──

def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, username: str, password: str) -> User:
    """Create a new user + empty profile."""
    user = User(username=username, password_hash=hash_password(password))
    db.add(user)
    db.flush()  # get user.id

    profile = Profile(user_id=user.id, name=username)
    db.add(profile)
    db.commit()
    db.refresh(user)
    return user


# ── Profile ──

def get_profile_by_user(db: Session, user_id: int) -> Profile | None:
    return db.query(Profile).filter(Profile.user_id == user_id).first()


def get_all_profiles(db: Session) -> list[Profile]:
    return db.query(Profile).options(joinedload(Profile.user)).all()


def upsert_profile(db: Session, user_id: int, data: dict) -> Profile:
    """Update the profile for a given user."""
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        profile = Profile(user_id=user_id)
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
    user_id: int | None = None,
    page: int = 1,
    limit: int = 10,
    q: str | None = None,
) -> tuple[list[Post], int]:
    """Get paginated posts, with optional type/user/search filter."""
    query = db.query(Post).options(joinedload(Post.user))

    if post_type:
        query = query.filter(Post.post_type == post_type)
    if user_id is not None:
        query = query.filter(Post.user_id == user_id)
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
    return db.query(Post).options(joinedload(Post.user)).filter(Post.id == post_id).first()


def create_post(db: Session, user_id: int, data: dict) -> Post:
    """Create a post owned by the given user."""
    post = Post(
        user_id=user_id,
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
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        return False
    db.delete(post)
    db.commit()
    return True
