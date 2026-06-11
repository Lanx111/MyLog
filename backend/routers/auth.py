"""Auth API routes: register, login, me."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas import UserRegister, UserLogin, ApiResponse
from crud import get_user_by_username, create_user
from auth_utils import verify_password, create_access_token
from dependencies import get_current_user
from models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register")
def register(body: UserRegister, db: Session = Depends(get_db)):
    """Register a new account. Returns JWT token."""
    existing = get_user_by_username(db, body.username)
    if existing:
        raise HTTPException(status_code=400, detail="用户名已被注册")

    user = create_user(db, body.username, body.password)
    token = create_access_token(user.id, user.username)
    return ApiResponse(data={
        "access_token": token,
        "token_type": "bearer",
        "user": user.to_dict(),
    }, message="注册成功")


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
