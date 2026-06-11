"""ORM models for the MyLog database."""
import json
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base


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
            "created_at": self.created_at.isoformat() if self.created_at else None,
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
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
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
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
