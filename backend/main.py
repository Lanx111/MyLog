"""MyLog v2 — Multi-user Personal Homepage & Growth Log System."""
import logging
import os
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from database import engine, Base
from routers import profile, posts, auth, admin, attachments
from auth_utils import check_access_session, decode_access_token

# ── Logging ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-5s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("mylog")

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MyLog API v2",
    description="Multi-user Personal Homepage & Growth Log System",
    version="2.0.0",
)

# ── CORS ──
# 通过环境变量 CORS_ORIGINS 配置允许的来源，多个域名用逗号分隔
# 示例: CORS_ORIGINS=http://localhost:5173,https://mylog.example.com
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Access gate middleware ──
# 如果未配置访问码，则跳过访问码检查（开发/测试环境）
ACCESS_CODE = os.getenv("ACCESS_CODE", "")
SKIP_ACCESS_GATE = not ACCESS_CODE

# 所有 /api/ 请求需携带有效 JWT 或 X-Access-Token（除白名单路径外）
ACCESS_WHITELIST = {"/", "/docs", "/openapi.json", "/redoc", "/favicon.ico"}
ACCESS_AUTH_SKIP = {"/api/auth/access", "/api/auth/login", "/api/auth/register"}


@app.middleware("http")
async def access_gate(request: Request, call_next):
    path = request.url.path

    # 白名单路径直接放行
    if path in ACCESS_WHITELIST:
        return await call_next(request)

    # 未配置访问码时（开发/测试环境），跳过门控检查
    if SKIP_ACCESS_GATE:
        return await call_next(request)

    # 只对 /api/ 路径做访问码检查
    if path.startswith("/api/"):
        # 登录/验证访问码接口不需要 token
        if path in ACCESS_AUTH_SKIP:
            return await call_next(request)

        # 检查 Authorization (JWT) — 已登录用户直接放行
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            jwt_payload = decode_access_token(auth_header[7:])
            if jwt_payload:
                return await call_next(request)

        # 检查 X-Access-Token — 通过访问码验证的访客
        access_token = request.headers.get("x-access-token", "")
        if access_token and check_access_session(access_token):
            return await call_next(request)

        # 都没有 → 拒绝
        return JSONResponse(
            status_code=403,
            content={"code": 403, "message": "需要访问码", "data": None},
        )

    return await call_next(request)


# ── Request logging middleware ──
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000
    client_ip = request.client.host if request.client else "-"
    logger.info(
        f"{client_ip}  {request.method:6s}  {request.url.path}  "
        f"{response.status_code}  {duration_ms:.0f}ms"
    )
    return response


# ── Routers ──
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(posts.router)
app.include_router(admin.router)
app.include_router(attachments.router)

# ── Static file serving for uploaded attachments ──
uploads_dir = Path(__file__).parent / "uploads"
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")


@app.get("/")
def root():
    return {"message": "MyLog API v2 is running", "docs": "/docs"}


# ── Global exception handlers ──
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    logger.warning(f"ValueError on {request.url.path}: {exc}")
    return JSONResponse(status_code=400, content={"code": 400, "message": str(exc), "data": None})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"code": 500, "message": "服务器内部错误", "data": None})
