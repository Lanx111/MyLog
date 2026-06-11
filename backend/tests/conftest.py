"""Shared fixtures for API tests."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, pool
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

# In-memory SQLite — StaticPool keeps all connections on the same DB
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=pool.StaticPool,
)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    """Fresh in-memory tables before each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Test client with test DB override."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth(client):
    """Register a test user, return (headers_dict, user_dict)."""
    resp = client.post("/api/auth/register", json={
        "username": "tester",
        "password": "test1234",
    })
    data = resp.json()["data"]
    return {
        "Authorization": f"Bearer {data['access_token']}",
    }, data["user"]


@pytest.fixture
def admin(client):
    """Register an admin user, return (headers_dict, user_dict)."""
    resp = client.post("/api/auth/register", json={
        "username": "admin",
        "password": "admin1234",
    })
    data = resp.json()["data"]

    # Set admin flag in DB
    db = TestingSession()
    from models import User
    user = db.query(User).filter(User.id == data["user"]["id"]).first()
    user.is_admin = True
    db.commit()
    db.close()

    return {
        "Authorization": f"Bearer {data['access_token']}",
    }, data["user"]
