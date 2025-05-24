from unittest.mock import patch

from fastapi.testclient import TestClient


from app.core.config import settings


def test_get_access_token(client: TestClient) -> None:
    login_data = {
        "username": "user55@example.com",
        "password": "stringst",
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]
