"""MyLog — Personal Homepage & Growth Log System API."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from database import engine, Base
from routers import profile, posts

# Create tables on startup if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MyLog API",
    description="Personal Homepage & Growth Log System — API documentation",
    version="1.0.0",
)

# CORS — allow all origins for development; restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(profile.router)
app.include_router(posts.router)


@app.get("/")
def root():
    return {"message": "MyLog API is running", "docs": "/docs"}


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(status_code=400, content={"code": 400, "message": str(exc), "data": None})
