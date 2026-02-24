from fastapi.testclient import TestClient

from core.config import settings


def test_health_status_code(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_response_body(client: TestClient):
    response = client.get("/health")
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == settings.APP_VERSION
    assert data["service"] == settings.APP_NAME


def test_health_db(client: TestClient):
    response = client.get("/api/v1/health/db")
    assert response.status_code == 200
    assert response.json() == {"database": "ok"}


def test_openapi_schema(client: TestClient):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "paths" in data
