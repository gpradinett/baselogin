from fastapi.testclient import TestClient
from sqlmodel import Session
from http import HTTPStatus

from app.core.config import settings
from app.models import UserCreate, UserRegister
from tests.factories import UserFactory, UserCreateFactory


def test_read_users(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    UserFactory.create_batch(2, session=db)
    response = client.get(
        f"{settings.API_V1_STR}/users/", headers=superuser_token_headers
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()["count"] > 1


def test_create_user_new_email(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    user_in = UserCreateFactory.build()
    response = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=superuser_token_headers,
        json=user_in.model_dump(mode='json', exclude={'create_at'}),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()["email"] == user_in.email


def test_signup_new_user(client: TestClient, db: Session) -> None:
    user_in = UserCreateFactory.build()
    response = client.post(
        f"{settings.API_V1_STR}/users/signup", json=user_in.model_dump(exclude={'create_at'})
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()["email"] == user_in.email
