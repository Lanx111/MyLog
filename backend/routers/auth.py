"""Auth API routes: login, access, me."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from schemas import UserLogin, ApiResponse
from crud import get_user_by_username
from auth_utils import verify_password, create_access_token, verify_access_code
from dependencies import get_current_user
from models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


class AccessRequest(BaseModel):
    code: str


@router.post("/access")
def verify_access(body: AccessRequest):
    """验证全站访问码，通过后返回 session token。"""
    token = verify_access_code(body.code)
    if not token:
        raise HTTPException(status_code=403, detail="访问码错误")
    return ApiResponse(data={"access_token": token}, message="验证通过")


@router.post("/login")
def login(body: UserLogin, db: Session = Depends(get_db)):
    """Login with username and password. Returns JWT token."""
    user = get_user_by_username(db, body.username)
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_access_token(user.id, user.username)
    return ApiResponse(data={
        "access_token": token,
        "token_type": "bearer",
        "user": user.to_dict(),
    }, message="登录成功")


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    """Get current logged-in user info."""
    return ApiResponse(data=current_user.to_dict())
