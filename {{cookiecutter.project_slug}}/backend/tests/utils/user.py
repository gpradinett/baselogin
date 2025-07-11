from fastapi.testclient import TestClient
from sqlmodel import Session

from app.crud import user as crud_user
from app.core.config import settings
from app.core.security import get_password_hash
from app.models import User, UserCreate, UserUpdate
from tests.factories import UserFactory, UserCreateFactory


def user_authentication_headers(
    *, client: TestClient, email: str, password: str
) -> dict[str, str]:
    """Generate authentication headers for a user.

    Args:
        client: The test client.
        email: The user's email.
        password: The user's password.

    Returns:
        A dictionary containing the Authorization header.
    """
    data = {"username": email, "password": password}

    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def create_random_user(db: Session) -> tuple[User, str]:
    """Create a random user.

    Args:
        db: The database session.

    Returns:
        A tuple containing the user and the password.
    """
    return UserFactory(session=db)


def authentication_token_from_email(
    *, client: TestClient, email: str, db: Session
) -> dict[str, str]:
    """Return a valid token for the user with given email.

    If the user doesn't exist it is created first.
    If the user exists, their password is updated and a new token is generated.

    Args:
        client: The test client.
        email: The user's email.
        db: The database session.

    Returns:
        A dictionary containing the Authorization header.
    """
    db_user = crud_user.get_user_by_email(session=db, email=email)
    if not db_user:
        user_in_create = UserCreateFactory.build(email=email)
        password = user_in_create.password
        user_to_create = User.model_validate(
            user_in_create,
            update={"hashed_password": get_password_hash(password)},
        )
        user = crud_user.create_user(session=db, user=user_to_create)
    else:
        password = UserCreateFactory.build().password
        user_in_update = UserUpdate(password=password)
        user_data = user_in_update.model_dump(exclude_unset=True)
        if "password" in user_data:
            hashed_password = get_password_hash(password)
            user_data["hashed_password"] = hashed_password
        if not db_user.id:
            raise Exception("User id not set")
        db_user = crud_user.update_user(
            session=db, db_user=db_user, user_data=user_data
        )

    return user_authentication_headers(client=client, email=email, password=password)
