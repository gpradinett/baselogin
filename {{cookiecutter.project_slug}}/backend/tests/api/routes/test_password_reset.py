from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.core.security import verify_password
from app.models import UserCreate, UserUpdate
from tests.utils.utils import random_email


def test_request_password_reset(client: TestClient, db: Session) -> None:
    email = random_email()
    password = "testpassword"
    user_in = UserCreate(email=email, password=password)
    crud.create_user(session=db, user_create=user_in)

    response = client.post(
        f"{settings.API_V1_STR}/password-reset/request-password-reset",
        params={"email": email},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Password reset email sent."}

    updated_user = crud.get_user_by_email(session=db, email=email)
    assert updated_user
    assert updated_user.password_reset_token is not None
    assert updated_user.password_reset_token_expires is not None


def test_reset_password_valid_token(client: TestClient, db: Session) -> None:
    email = random_email()
    password = "testpassword"
    user_in = UserCreate(email=email, password=password)
    user = crud.create_user(session=db, user_create=user_in)

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
    assert response.status_code == 200
    assert response.json() == {"message": "Password reset successfully."}

    updated_user = crud.get_user_by_email(session=db, email=email)
    assert updated_user
    assert updated_user.password_reset_token is None
    assert updated_user.password_reset_token_expires is None
    assert verify_password(new_password, updated_user.hashed_password)


def test_reset_password_invalid_token(client: TestClient, db: Session) -> None:
    email = random_email()
    password = "testpassword"
    user_in = UserCreate(email=email, password=password)
    crud.create_user(session=db, user_create=user_in)

    response = client.post(
        f"{settings.API_V1_STR}/password-reset/reset-password",
        json={
            "token": "invalid_token",
            "new_password": "newtestpassword",
        },
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid token."}


def test_reset_password_expired_token(client: TestClient, db: Session) -> None:
    email = random_email()
    password = "testpassword"
    user_in = UserCreate(email=email, password=password)
    user = crud.create_user(session=db, user_create=user_in)

    # Simulate requesting a password reset with an expired token
    token = "test_expired_token"
    expires = datetime.now(timezone.utc) - timedelta(minutes=30)
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
    assert response.status_code == 400
    assert response.json() == {"detail": "Token expired."}
