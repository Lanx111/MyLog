"""ORM models for the MyLog database."""
import json
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime
from database import Base


class Profile(Base):
    """Personal profile — single-row table that stores the user's info."""

    __tablename__ = "profile"

    id = Column(Integer, primary_key=True, default=1)
    name = Column(String(100), default="")
    title = Column(String(200), default="")
    avatar_url = Column(Text, default="")
    bio = Column(Text, default="")
    skills = Column(Text, default="[]")  # JSON array stored as text
    github_url = Column(Text, default="")
    blog_url = Column(Text, default="")
    email = Column(String(200), default="")
    learning_goals = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def skills_list(self) -> list:
        return json.loads(self.skills) if self.skills else []

    @skills_list.setter
    def skills_list(self, value: list):
        self.skills = json.dumps(value, ensure_ascii=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
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
    """A work log, study log, daily report, or summary."""

    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(300), nullable=False)
    content = Column(Text, default="")
    post_type = Column(String(20), default="work_log")  # work_log | study_log | daily_report | weekly_report | summary
    tags = Column(Text, default="[]")  # JSON array stored as text
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def tags_list(self) -> list:
        return json.loads(self.tags) if self.tags else []

    @tags_list.setter
    def tags_list(self, value: list):
        self.tags = json.dumps(value, ensure_ascii=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "post_type": self.post_type,
            "tags": self.tags_list,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
