import uuid
from datetime import timedelta
from typing import Any, Generator

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.api.deps import get_current_active_superuser, get_current_user, get_db
from app.core import security
from app.core.config import settings
from app.models import User
from tests.factories import UserFactory

# Create a temporary FastAPI app to test dependencies
app = FastAPI()

# This is the key change: Override the get_db dependency
# to ensure the tests and the app use the same DB session.
def get_db_override() -> Generator[Session, None, None]:
    # This is a dummy override. The actual session will be provided by the fixture.
    # We will use app.dependency_overrides to inject the test session.
    yield from get_db() # This will be replaced by the test fixture

app.dependency_overrides[get_db] = get_db_override


@app.get("/test-current-user")
def route_with_current_user(current_user: User = Depends(get_current_user)) -> Any:
    return {"user_id": str(current_user.id)}


@app.get("/test-superuser")
def route_with_superuser(
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    return {"user_id": str(current_user.id)}


client = TestClient(app)


def test_get_current_user_invalid_token(db: Session) -> None:
    """Test dependency with an invalid token."""
    app.dependency_overrides[get_db] = lambda: db
    response = client.get(
        "/test-current-user", headers={"Authorization": "Bearer invalidtoken"}
    )
    app.dependency_overrides = {}
    assert response.status_code == 403
    assert response.json() == {"detail": "Could not validate credentials"}


def test_get_current_user_nonexistent_user(db: Session) -> None:
    """Test dependency with a token for a non-existent user."""
    app.dependency_overrides[get_db] = lambda: db
    non_existent_uuid = uuid.uuid4()
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(
        str(non_existent_uuid), expires_delta=expires_delta
    )
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/test-current-user", headers=headers)
    app.dependency_overrides = {}
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_get_current_user_inactive(db: Session) -> None:
    """Test dependency with an inactive user."""
    app.dependency_overrides[get_db] = lambda: db
    user, _ = UserFactory(session=db, is_active=False)

    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(user.id, expires_delta=expires_delta)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/test-current-user", headers=headers)
    app.dependency_overrides = {}
    assert response.status_code == 400
    assert response.json() == {"detail": "Inactive user"}


def test_get_current_active_superuser_normal_user(db: Session) -> None:
    """Test superuser dependency with a normal user."""
    app.dependency_overrides[get_db] = lambda: db
    user, _ = UserFactory(session=db, is_superuser=False)

    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(user.id, expires_delta=expires_delta)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/test-superuser", headers=headers)
    app.dependency_overrides = {}
    assert response.status_code == 403
    assert response.json() == {"detail": "The user doesn't have enough privileges"}


def test_get_current_active_superuser_success(db: Session) -> None:
    """Test superuser dependency with a superuser."""
    app.dependency_overrides[get_db] = lambda: db
    user, _ = UserFactory(session=db, is_superuser=True)

    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(user.id, expires_delta=expires_delta)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/test-superuser", headers=headers)
    app.dependency_overrides = {}
    assert response.status_code == 200
    assert response.json() == {"user_id": str(user.id)}

