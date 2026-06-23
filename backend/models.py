"""ORM models for the MyLog database."""
import json
import os
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base


def _to_iso(dt: datetime | None) -> str | None:
    """Convert datetime to ISO string with UTC timezone suffix.

    SQLite strips timezone info on storage, so datetimes read back as naive.
    Append '+00:00' to ensure the frontend interprets them as UTC, not local time.
    """
    if dt is None:
        return None
    s = dt.isoformat()
    # If no timezone indicator present, append UTC offset
    if not s.endswith('Z') and '+' not in s[11:] and '-' not in s[11:]:
        s += '+00:00'
    return s


class User(Base):
    """Registered user account."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False)
    posts = relationship("Post", back_populates="user")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "is_admin": self.is_admin,
            "created_at": _to_iso(self.created_at),
        }


class Profile(Base):
    """Personal profile — one per user."""

    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String(100), default="")
    title = Column(String(200), default="")
    avatar_url = Column(Text, default="")
    bio = Column(Text, default="")
    skills = Column(Text, default="[]")
    github_url = Column(Text, default="")
    blog_url = Column(Text, default="")
    email = Column(String(200), default="")
    learning_goals = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="profile")

    @property
    def skills_list(self) -> list:
        return json.loads(self.skills) if self.skills else []

    @skills_list.setter
    def skills_list(self, value: list):
        self.skills = json.dumps(value, ensure_ascii=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.user.username if self.user else None,
            "name": self.name,
            "title": self.title,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "skills": self.skills_list,
            "github_url": self.github_url,
            "blog_url": self.blog_url,
            "email": self.email,
            "learning_goals": self.learning_goals,
            "created_at": _to_iso(self.created_at),
            "updated_at": _to_iso(self.updated_at),
        }


class Post(Base):
    """A work log, study log, daily report, weekly report, or summary."""

    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(300), nullable=False)
    content = Column(Text, default="")
    post_type = Column(String(20), default="work_log")
    tags = Column(Text, default="[]")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="posts")
    attachments = relationship("Attachment", back_populates="post", cascade="all, delete-orphan")

    @property
    def tags_list(self) -> list:
        return json.loads(self.tags) if self.tags else []

    @tags_list.setter
    def tags_list(self, value: list):
        self.tags = json.dumps(value, ensure_ascii=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "author": self.user.username if self.user else None,
            "title": self.title,
            "content": self.content,
            "post_type": self.post_type,
            "tags": self.tags_list,
            "created_at": _to_iso(self.created_at),
            "updated_at": _to_iso(self.updated_at),
            "attachments": [a.to_dict() for a in self.attachments] if self.attachments else [],
        }


class Attachment(Base):
    """Uploaded file attached to a post — image or document."""

    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(300), nullable=False)
    stored_name = Column(String(300), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, default=0)
    file_type = Column(String(20), nullable=False, default="attachment")  # "image" | "attachment"
    mime_type = Column(String(100), default="application/octet-stream")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    post = relationship("Post", back_populates="attachments")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "post_id": self.post_id,
            "filename": self.filename,
            "url": f"/uploads/{self.stored_name}",
            "file_size": self.file_size,
            "file_type": self.file_type,
            "mime_type": self.mime_type,
            "created_at": _to_iso(self.created_at),
        }
