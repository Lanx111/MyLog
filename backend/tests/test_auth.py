"""Tests for auth endpoints."""
import pytest


class TestAuth:
    def test_register_creates_user_and_returns_token(self, client):
        resp = client.post("/api/auth/register", json={
            "username": "newuser",
            "password": "pass1234",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == 0
        assert data["data"]["access_token"]
        assert data["data"]["user"]["username"] == "newuser"
        assert data["data"]["user"]["is_admin"] is False
        assert "password_hash" not in data["data"]["user"]

    def test_register_duplicate_username_fails(self, client):
        client.post("/api/auth/register", json={
            "username": "dup", "password": "pass1234",
        })
        resp = client.post("/api/auth/register", json={
            "username": "dup", "password": "pass5678",
        })
        assert resp.status_code == 400
        assert "已被注册" in resp.json()["detail"]

    def test_register_short_password_fails(self, client):
        resp = client.post("/api/auth/register", json={
            "username": "x", "password": "12",
        })
        assert resp.status_code == 422

    def test_login_with_correct_credentials(self, client):
        client.post("/api/auth/register", json={
            "username": "user1", "password": "correct1",
        })
        resp = client.post("/api/auth/login", json={
            "username": "user1", "password": "correct1",
        })
        assert resp.status_code == 200
        assert resp.json()["data"]["access_token"]

    def test_login_with_wrong_password(self, client):
        client.post("/api/auth/register", json={
            "username": "user2", "password": "right1234",
        })
        resp = client.post("/api/auth/login", json={
            "username": "user2", "password": "wrong",
        })
        assert resp.status_code == 401

    def test_me_returns_current_user(self, client, auth):
        headers, user = auth
        resp = client.get("/api/auth/me", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["username"] == "tester"

    def test_me_without_token_returns_401(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401


class TestProfile:
    def test_register_auto_creates_profile(self, client, auth):
        headers, user = auth
        resp = client.get("/api/profile", headers=headers)
        assert resp.status_code == 200
        p = resp.json()["data"]
        assert p["user_id"] == user["id"]
        assert p["username"] == "tester"

    def test_update_profile(self, client, auth):
        headers, user = auth
        resp = client.put("/api/profile", json={
            "name": "Test User",
            "title": "Developer",
            "skills": ["Python", "React"],
            "bio": "Hello world",
        }, headers=headers)
        assert resp.status_code == 200
        p = resp.json()["data"]
        assert p["name"] == "Test User"
        assert p["title"] == "Developer"
        assert p["skills"] == ["Python", "React"]

    def test_profiles_public(self, client, auth):
        headers, user = auth
        client.post("/api/auth/register", json={
            "username": "other", "password": "pass1234",
        })
        resp = client.get("/api/profiles")
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 2
