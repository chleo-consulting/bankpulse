from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from core.security import create_access_token
from model.models import User


@pytest.fixture
def test_user(db_session) -> User:
    user = User(
        email=f"cat_{uuid4().hex[:8]}@example.com",
        password_hash="hashed",
    )
    db_session.add(user)
    db_session.flush()
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    token = create_access_token(str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


class TestListCategories:
    def test_list_returns_200(
        self, client: TestClient, auth_headers: dict, seed_categories
    ) -> None:
        response = client.get("/api/v1/categories", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_list_hierarchical_structure(
        self, client: TestClient, auth_headers: dict, seed_categories
    ) -> None:
        response = client.get("/api/v1/categories", headers=auth_headers)
        data = response.json()
        alimentation = next((c for c in data if c["name"] == "Alimentation"), None)
        assert alimentation is not None
        assert "children" in alimentation
        children_names = [c["name"] for c in alimentation["children"]]
        assert "Supermarché" in children_names

    def test_list_children_have_parent_id(
        self, client: TestClient, auth_headers: dict, seed_categories
    ) -> None:
        response = client.get("/api/v1/categories", headers=auth_headers)
        data = response.json()
        alimentation = next((c for c in data if c["name"] == "Alimentation"), None)
        assert alimentation is not None
        for child in alimentation["children"]:
            assert child["parent_id"] is not None
            assert child["parent_id"] == alimentation["id"]

    def test_list_requires_auth(self, client: TestClient) -> None:
        response = client.get("/api/v1/categories")
        assert response.status_code == 401

    def test_list_empty_without_seed(self, client: TestClient, auth_headers: dict) -> None:
        """Sans seed, la liste doit être vide (ou contenir seulement ce qui est en DB)."""
        response = client.get("/api/v1/categories", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
