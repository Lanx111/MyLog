"""Tests for post endpoints and permission isolation."""
import pytest


class TestPosts:
    def test_create_post(self, client, auth):
        headers, user = auth
        resp = client.post("/api/posts", json={
            "title": "My first post",
            "content": "Hello",
            "post_type": "work_log",
            "tags": ["test"],
        }, headers=headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["title"] == "My first post"
        assert data["author"] == "tester"
        assert data["user_id"] == user["id"]

    def test_create_post_without_auth_fails(self, client):
        resp = client.post("/api/posts", json={
            "title": "No auth",
            "content": "Should fail",
        })
        assert resp.status_code == 401

    def test_list_posts_public(self, client, auth):
        headers, user = auth
        client.post("/api/posts", json={
            "title": "Post 1", "content": "A",
        }, headers=headers)
        client.post("/api/posts", json={
            "title": "Post 2", "content": "B",
        }, headers=headers)

        resp = client.get("/api/posts")
        assert resp.status_code == 200
        items = resp.json()["data"]["items"]
        assert len(items) == 2

    def test_filter_by_type(self, client, auth):
        headers, user = auth
        client.post("/api/posts", json={
            "title": "Work", "post_type": "work_log",
        }, headers=headers)
        client.post("/api/posts", json={
            "title": "Study", "post_type": "study_log",
        }, headers=headers)

        resp = client.get("/api/posts?post_type=work_log")
        items = resp.json()["data"]["items"]
        assert len(items) == 1
        assert items[0]["title"] == "Work"

    def test_filter_by_user(self, client, auth):
        headers, user = auth
        client.post("/api/posts", json={
            "title": "From tester",
        }, headers=headers)

        resp = client.get(f"/api/posts?user_id={user['id']}")
        items = resp.json()["data"]["items"]
        assert len(items) == 1
        assert items[0]["author"] == "tester"

    def test_pagination(self, client, auth):
        headers, user = auth
        for i in range(5):
            client.post("/api/posts", json={
                "title": f"Post {i}",
            }, headers=headers)

        resp = client.get("/api/posts?limit=2&page=1")
        data = resp.json()["data"]
        assert len(data["items"]) == 2
        assert data["total"] == 5

    def test_cannot_delete_others_post(self, client, auth):
        headers, user = auth
        # Create user2
        resp2 = client.post("/api/auth/register", json={
            "username": "user2", "password": "1234",
        })
        token2 = resp2.json()["data"]["access_token"]
        h2 = {"Authorization": f"Bearer {token2}"}

        # user2 creates a post
        resp = client.post("/api/posts", json={
            "title": "User2's post",
        }, headers=h2)
        post_id = resp.json()["data"]["id"]

        # tester tries to delete user2's post → 403
        resp = client.delete(f"/api/posts/{post_id}", headers=headers)
        assert resp.status_code == 403

    def test_can_delete_own_post(self, client, auth):
        headers, user = auth
        resp = client.post("/api/posts", json={
            "title": "My post",
        }, headers=headers)
        post_id = resp.json()["data"]["id"]

        resp = client.delete(f"/api/posts/{post_id}", headers=headers)
        assert resp.status_code == 200

    def test_weekly_report_type_accepted(self, client, auth):
        headers, user = auth
        resp = client.post("/api/posts", json={
            "title": "Weekly",
            "post_type": "weekly_report",
        }, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["post_type"] == "weekly_report"


class TestAdmin:
    def test_admin_can_list_users(self, client, admin):
        headers, user = admin
        # Create another user
        client.post("/api/auth/register", json={
            "username": "normal", "password": "1234",
        })

        resp = client.get("/api/admin/users", headers=headers)
        assert resp.status_code == 200
        users = resp.json()["data"]
        assert len(users) >= 2

    def test_non_admin_cannot_access_admin_api(self, client, auth):
        headers, user = auth
        resp = client.get("/api/admin/users", headers=headers)
        assert resp.status_code == 403

    def test_admin_can_delete_user(self, client, admin):
        headers, user = admin
        # Create a user to delete
        resp = client.post("/api/auth/register", json={
            "username": "victim", "password": "1234",
        })
        uid = resp.json()["data"]["user"]["id"]

        resp = client.delete(f"/api/admin/users/{uid}", headers=headers)
        assert resp.status_code == 200
        assert "已删除" in resp.json()["message"]

    def test_admin_cannot_delete_self(self, client, admin):
        headers, user = admin
        resp = client.delete(f"/api/admin/users/{user['id']}", headers=headers)
        assert resp.status_code == 400
