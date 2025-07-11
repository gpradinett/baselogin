from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel

from app.crud import user as crud_user
from app.crud import client as crud_client
from app.api.deps import get_db
from app.core.config import settings
from app.core.db import engine, init_db
from app.main import app
from app.models import UserCreate, Client, ClientCreate, User
from tests.utils.user import authentication_token_from_email


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def superuser_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    init_db(db)
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


@pytest.fixture(scope="function")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )


@pytest.fixture(scope="function")
def normal_user(db: Session) -> User:
    user_in = UserCreate(
        email="normal_user@example.com",
        password="password123",
        full_name="Normal User",
    )
    user = crud_user.create_user(session=db, user_create=user_in)
    return user


@pytest.fixture(scope="function")
def superuser(db: Session) -> User:
    init_db(db)
    user = crud_user.get_user_by_email(session=db, email=settings.FIRST_SUPERUSER)
    if not user:
        raise Exception("Superuser not found")
    return user


@pytest.fixture(scope="function")
def test_client(db: Session, superuser_token_headers: dict[str, str]) -> Client:
    client_in = ClientCreate(name="Test App", redirect_uris=["http://localhost/callback"], scopes=["read", "write"])
    # We need to get the superuser ID from the token to set as owner_id
    # This is a simplified way, in a real app you might decode the token or get the user from DB
    # For testing, we can assume the superuser is created by init_db
    superuser = crud_user.get_user_by_email(session=db, email=settings.FIRST_SUPERUSER)
    if not superuser:
        raise Exception("Superuser not found for test client creation")
    
    created_client, _ = crud_client.create_client(session=db, client_create=client_in, owner_id=superuser.id)
    return created_client