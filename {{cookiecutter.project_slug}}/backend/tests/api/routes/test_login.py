from http import HTTPStatus
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from tests.factories import UserFactory


def test_get_access_token(client: TestClient, db: Session) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    assert r.status_code == HTTPStatus.OK
    assert "access_token" in tokens
    assert tokens["access_token"]


def test_authenticate_user_not_found(client: TestClient, db: Session) -> None:
    login_data = {
        "username": "nonexistent@example.com",
        "password": "testpassword",
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    assert r.status_code == HTTPStatus.BAD_REQUEST
    assert r.json()["detail"] == "Incorrect email or password"


def test_authenticate_incorrect_password(client: TestClient, db: Session) -> None:
    user, plain_password = UserFactory(session=db)
    login_data = {
        "username": user.email,
        "password": "wrongpassword",
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    assert r.status_code == HTTPStatus.BAD_REQUEST
    assert r.json()["detail"] == "Incorrect email or password"


def test_authenticate_inactive_user(client: TestClient, db: Session) -> None:
    user, plain_password = UserFactory(session=db, is_active=False)
    login_data = {
        "username": user.email,
        "password": plain_password,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    assert r.status_code == HTTPStatus.BAD_REQUEST
    assert r.json()["detail"] == "Inactive user"