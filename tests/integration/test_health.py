"""Tests for health endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestHealth:
    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["application"] == "ok"
        assert "database" in data
        assert "s3" in data
        assert "ai" in data

    def test_health_database(self):
        response = client.get("/health/database")
        assert response.status_code == 200
        assert "status" in response.json()

    def test_health_s3(self):
        response = client.get("/health/s3")
        assert response.status_code == 200
        assert "status" in response.json()

    def test_upload_page_loads(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "Upload Document" in response.text

    def test_search_page_loads(self):
        response = client.get("/search")
        assert response.status_code == 200
        assert "Search Knowledge Base" in response.text
