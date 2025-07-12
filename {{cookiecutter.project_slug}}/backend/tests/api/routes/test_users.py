from fastapi.testclient import TestClient
from sqlmodel import Session
from http import HTTPStatus

from app.core.config import settings
from app.models import UserUpdate, User
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


def test_create_user_existing_email(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    user, _ = UserFactory(session=db)
    user_in = UserCreateFactory.build(email=user.email)
    response = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=superuser_token_headers,
        json=user_in.model_dump(mode='json', exclude={'create_at'}),
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "The user with this email already exists" in response.json()["detail"]


def test_signup_new_user(client: TestClient, db: Session) -> None:
    user_in = UserCreateFactory.build()
    response = client.post(
        f"{settings.API_V1_STR}/users/signup", json=user_in.model_dump(exclude={'create_at'})
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()["email"] == user_in.email


def test_update_user(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    user, _ = UserFactory(session=db)
    new_full_name = "New Full Name"
    user_update = UserUpdate(full_name=new_full_name)
    response = client.patch(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=superuser_token_headers,
        json=user_update.model_dump(mode='json', exclude_unset=True),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()["full_name"] == new_full_name


def test_update_user_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    user_update = UserUpdate(full_name="Non Existent")
    response = client.patch(
        f"{settings.API_V1_STR}/users/{non_existent_id}",
        headers=superuser_token_headers,
        json=user_update.model_dump(mode='json', exclude_unset=True),
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert "The user with this username does not exist in the system." in response.json()["detail"]


def test_update_user_existing_email(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    user1, _ = UserFactory(session=db)
    user2, _ = UserFactory(session=db)
    user_update = UserUpdate(email=user2.email)
    response = client.patch(
        f"{settings.API_V1_STR}/users/{user1.id}",
        headers=superuser_token_headers,
        json=user_update.model_dump(mode='json', exclude_unset=True),
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "The user with this email already exists" in response.json()["detail"]


def test_delete_user(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    user, _ = UserFactory(session=db)
    response = client.delete(
        f"{settings.API_V1_STR}/users/{user.id}", headers=superuser_token_headers
    )
    assert response.status_code == HTTPStatus.OK
    response_user = response.json()
    assert response_user["id"] == str(user.id)
    assert response_user["email"] == user.email


def test_delete_user_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    response = client.delete(
        f"{settings.API_V1_STR}/users/{non_existent_id}", headers=superuser_token_headers
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert "The user with this username does not exist in the system." in response.json()["detail"]


def test_delete_self_superuser(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "Superusers can't delete themselves." in response.json()["detail"]


def test_delete_user_self_superuser(
    client: TestClient, superuser_token_headers: dict[str, str], superuser: User
) -> None:
    response = client.delete(
        f"{settings.API_V1_STR}/users/{superuser.id}", headers=superuser_token_headers
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "Superusers can't delete themselves." in response.json()["detail"]