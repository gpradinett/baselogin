import pytest
from datetime import datetime, timedelta, timezone
from http import HTTPStatus

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.crud import user as crud_user
from app.core.config import settings
from app.core.security import verify_password
from tests.factories import UserFactory, UserCreateFactory


def test_request_password_reset(client: TestClient, db: Session) -> None:
    user_in = UserCreateFactory.build()
    crud_user.create_user(session=db, user_create=user_in)

    response = client.post(
        f"{settings.API_V1_STR}/password-reset/request-password-reset",
        params={"email": user_in.email},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Password reset email sent."}

    updated_user = crud_user.get_user_by_email(session=db, email=user_in.email)
    assert updated_user
    assert updated_user.password_reset_token is not None
    assert updated_user.password_reset_token_expires is not None


def test_reset_password_valid_token(client: TestClient, db: Session) -> None:
    user, plain_password = UserFactory(session=db)

    # Simulate requesting a password reset
    token = "test_valid_token"
    expires = datetime.now(timezone.utc) + timedelta(minutes=30)
    user.password_reset_token = token
    user.password_reset_token_expires = expires
    db.add(user)

    new_password = "newtestpassword"
    response = client.post(
        f"{settings.API_V1_STR}/password-reset/reset-password",
        json={
            "token": token,
            "new_password": new_password,
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Password reset successfully."}

    updated_user = crud_user.get_user_by_email(session=db, email=user.email)
    assert updated_user
    assert updated_user.password_reset_token is None
    assert updated_user.password_reset_token_expires is None
    assert verify_password(new_password, updated_user.hashed_password)


@pytest.mark.parametrize(
    "token, expected_detail, is_expired",
    [
        ("invalid_token", "Invalid token.", False),
        ("test_expired_token", "Token expired.", True),
    ],
)
def test_reset_password_invalid_or_expired_token(
    client: TestClient, db: Session, token: str, expected_detail: str, is_expired: bool
) -> None:
    user, plain_password = UserFactory(session=db)

    if is_expired:
        user.password_reset_token = token
        user.password_reset_token_expires = datetime.now(timezone.utc) - timedelta(
            minutes=30
        )
        db.add(user)

    new_password = "newtestpassword"
    response = client.post(
        f"{settings.API_V1_STR}/password-reset/reset-password",
        json={
            "token": token,
            "new_password": new_password,
        },
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {"detail": expected_detail}