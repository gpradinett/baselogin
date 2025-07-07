from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import User
from tests.factories import UserCreateFactory
from tests.utils.user import (
    authentication_token_from_email,
    create_random_user,
)


def test_create_random_user(db: Session) -> None:
    """
    Test creating a random user utility.
    """
    user, password = create_random_user(db)
    assert user
    assert password
    assert user.email
    db_user = crud.get_user_by_email(session=db, email=user.email)
    assert db_user
    assert db_user.email == user.email


def test_authentication_token_from_email_new_user(
    client: TestClient, db: Session
) -> None:
    """
    Test getting an authentication token for a new user.
    """
    email = "new_test@example.com"
    headers = authentication_token_from_email(client=client, email=email, db=db)
    assert "Authorization" in headers
    assert headers["Authorization"].startswith("Bearer ")


def test_authentication_token_from_email_existing_user(
    client: TestClient, db: Session
) -> None:
    """
    Test getting an authentication token for an existing user.
    This should update the user's password.
    """
    # 1. Create an existing user
    password_before = "old_password123"
    user_in_create = UserCreateFactory.build(password=password_before)
    user = crud.create_user(session=db, user_create=user_in_create)

    # 2. Get token for the existing user
    headers = authentication_token_from_email(client=client, email=user.email, db=db)
    assert "Authorization" in headers

    # 3. Verify password has been updated
    db.refresh(user)
    assert not crud.verify_password(password_before, user.hashed_password)
