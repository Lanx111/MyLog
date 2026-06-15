"""JWT token and password utilities (stdlib-only hashing)."""
import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from jose import JWTError, jwt

# 自动加载 backend/.env 文件（开发环境）
load_dotenv(Path(__file__).parent / ".env")

SECRET_KEY = os.getenv("JWT_SECRET", "")
if not SECRET_KEY:
    raise RuntimeError("必须设置 JWT_SECRET 环境变量，请检查 .env 或系统环境变量配置")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# 全站访问码（访客浏览用，非登录）
ACCESS_CODE = os.getenv("ACCESS_CODE", "")


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2 + SHA256 with a random salt."""
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    return f"{salt}${dk.hex()}"


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against a pbkdf2 hash."""
    salt, hash_val = hashed.split("$", 1)
    dk = hashlib.pbkdf2_hmac("sha256", plain.encode(), salt.encode(), 100000)
    return secrets.compare_digest(dk.hex(), hash_val)


def create_access_token(user_id: int, username: str) -> str:
    """Create a JWT access token."""
    expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {"sub": str(user_id), "username": username, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Decode and validate a JWT token. Returns payload or None."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


# ── 全站访问码 ──

def create_access_session() -> str:
    """为验证通过的访客生成一个签名 session token（有效期 7 天）。"""
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    payload = {"type": "access_session", "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_access_code(code: str) -> str | None:
    """验证访问码，通过则返回 session token，否则返回 None。"""
    if not ACCESS_CODE:
        return None
    if not secrets.compare_digest(code, ACCESS_CODE):
        return None
    return create_access_session()


def check_access_session(token: str) -> bool:
    """校验访客的 access session token 是否有效。"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("type") == "access_session"
    except JWTError:
        return False
