"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


# ── Generic response wrapper ──

class ApiResponse(BaseModel):
    code: int = 0
    message: str = "ok"
    data: Any = None


class PaginatedData(BaseModel):
    items: List[Any]
    total: int
    page: int
    limit: int


# ── Profile ──

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[List[str]] = None
    github_url: Optional[str] = None
    blog_url: Optional[str] = None
    email: Optional[str] = None
    learning_goals: Optional[str] = None


# ── Posts ──

class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    content: str = ""
    post_type: str = Field(default="work_log", pattern=r"^(work_log|study_log|daily_report|weekly_report|summary)$")
    tags: Optional[List[str]] = []


class PostUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=300)
    content: Optional[str] = None
    post_type: Optional[str] = Field(default=None, pattern=r"^(work_log|study_log|daily_report|weekly_report|summary)$")
    tags: Optional[List[str]] = None


class PostListQuery(BaseModel):
    post_type: Optional[str] = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)
    q: Optional[str] = None  # search keyword
