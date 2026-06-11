"""MyLog v2 — Multi-user Personal Homepage & Growth Log System."""
import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from database import engine, Base
from routers import profile, posts, auth, admin

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
