from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models import UserCreate, UserRegister
from app.crud import create_user
from tests.utils.user import create_random_user
from tests.utils.utils import random_email


def test_read_users(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    create_random_user(db=db)
    create_random_user(db=db)
    response = client.get(
        f"{settings.API_V1_STR}/users/", headers=superuser_token_headers
    )
    assert response.status_code == 200
    assert response.json()["count"] > 1


def test_create_user_new_email(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    email = random_email()
    password = "testpassword"
    user_in = UserCreate(email=email, password=password)
    response = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=superuser_token_headers,
        json=user_in.model_dump(mode='json'),
    )
    assert response.status_code == 200
    assert response.json()["email"] == email


def test_signup_new_user(client: TestClient, db: Session) -> None:
    email = random_email()
    password = "testpassword"
    user_in = UserRegister(email=email, password=password)
    response = client.post(
        f"{settings.API_V1_STR}/users/signup", json=user_in.model_dump()
    )
    assert response.status_code == 200
    assert response.json()["email"] == email
