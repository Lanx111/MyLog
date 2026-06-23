"""Pydantic schemas for request/response validation."""
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


# ── Auth ──

class UserRegister(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    username: str
    password: str


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


# ── Attachments ──

class AttachmentResponse(BaseModel):
    id: int
    post_id: int
    filename: str
    url: str
    file_size: int
    file_type: str
    mime_type: str
    created_at: Optional[str] = None
