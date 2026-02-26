from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from core.security import create_access_token
from model.models import Tag, User


@pytest.fixture
def test_user(db_session) -> User:
    user = User(
        email=f"tags_{uuid4().hex[:8]}@example.com",
        password_hash="hashed",
    )
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    token = create_access_token(str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


class TestListTags:
    def test_list_returns_200(self, client: TestClient, auth_headers: dict) -> None:
        response = client.get("/api/v1/tags", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_returns_existing_tags(
        self, client: TestClient, auth_headers: dict, db_session
    ) -> None:
        tag = Tag(name=f"list_tag_{uuid4().hex[:6]}")
        db_session.add(tag)
        db_session.flush()

        response = client.get("/api/v1/tags", headers=auth_headers)
        names = [t["name"] for t in response.json()]
        assert tag.name in names

    def test_list_requires_auth(self, client: TestClient) -> None:
        response = client.get("/api/v1/tags")
        assert response.status_code == 401


class TestCreateTag:
    def test_create_tag_returns_201(self, client: TestClient, auth_headers: dict) -> None:
        name = f"newtag_{uuid4().hex[:6]}"
        response = client.post("/api/v1/tags", json={"name": name}, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == name
        assert "id" in data
        assert "created_at" in data

    def test_create_tag_duplicate_returns_409(self, client: TestClient, auth_headers: dict) -> None:
        name = f"dup_{uuid4().hex[:6]}"
        client.post("/api/v1/tags", json={"name": name}, headers=auth_headers)
        response = client.post("/api/v1/tags", json={"name": name}, headers=auth_headers)
        assert response.status_code == 409

    def test_create_tag_requires_auth(self, client: TestClient) -> None:
        response = client.post("/api/v1/tags", json={"name": "unauth"})
        assert response.status_code == 401

    def test_created_tag_appears_in_list(self, client: TestClient, auth_headers: dict) -> None:
        name = f"appear_{uuid4().hex[:6]}"
        client.post("/api/v1/tags", json={"name": name}, headers=auth_headers)
        list_resp = client.get("/api/v1/tags", headers=auth_headers)
        names = [t["name"] for t in list_resp.json()]
        assert name in names
