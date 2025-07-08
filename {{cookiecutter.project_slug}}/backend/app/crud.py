from typing import Any
import uuid # Added this import

from sqlmodel import Session, select
from sqlalchemy import func

from app.core.security import get_password_hash, verify_password
from app.models import User, UserCreate, UserUpdate, Client, ClientCreate, ClientUpdate


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def get_multiple_users(*, session: Session, skip: int, limit: int) -> dict[str, Any]:
    count_statement = select(func.count()).select_from(User)
    count = session.scalar(count_statement)

    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()

    return {"data": users, "count": count}

def get_user_by_password_reset_token(*, session: Session, token: str) -> User | None:
    statement = select(User).where(User.password_reset_token == token)
    user = session.exec(statement).first()
    return user


# CRUD operations for Client model

def create_client(*, session: Session, client_create: ClientCreate, owner_id: str) -> Client:
    """
    Creates a new client in the database.

    Args:
        session: The database session.
        client_create: The client data to create.
        owner_id: The ID of the user who owns this client.

    Returns:
        The created Client object.
    """
    # Generate a random client_secret for the new client
    client_secret = str(uuid.uuid4())
    db_obj = Client.model_validate(
        client_create,
        update={
            "hashed_client_secret": get_password_hash(client_secret),
            "owner_id": owner_id,
        },
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    # Return the client object along with the unhashed client_secret
    # The unhashed secret should only be returned once upon creation
    return db_obj, client_secret


def get_client_by_client_id(*, session: Session, client_id: str) -> Client | None:
    """
    Retrieves a client by its client_id.

    Args:
        session: The database session.
        client_id: The client_id of the client to retrieve.

    Returns:
        The Client object if found, otherwise None.
    """
    statement = select(Client).where(Client.client_id == client_id)
    session_client = session.exec(statement).first()
    return session_client


def update_client(*, session: Session, db_client: Client, client_in: ClientUpdate) -> Client:
    """
    Updates an existing client in the database.

    Args:
        session: The database session.
        db_client: The existing Client object from the database.
        client_in: The updated client data.

    Returns:
        The updated Client object.
    """
    client_data = client_in.model_dump(exclude_unset=True)
    db_client.sqlmodel_update(client_data)
    session.add(db_client)
    session.commit()
    session.refresh(db_client)
    return db_client


def delete_client(*, session: Session, db_client: Client) -> None:
    """
    Deletes a client from the database.

    Args:
        session: The database session.
        db_client: The Client object to delete.
    """
    session.delete(db_client)
    session.commit()


def get_multiple_clients(*, session: Session, skip: int, limit: int) -> dict[str, Any]:
    """
    Retrieves multiple clients from the database with pagination.

    Args:
        session: The database session.
        skip: The number of records to skip.
        limit: The maximum number of records to return.

    Returns:
        A dictionary containing a list of Client objects and the total count.
    """
    count_statement = select(func.count()).select_from(Client)
    count = session.scalar(count_statement)

    statement = select(Client).offset(skip).limit(limit)
    clients = session.exec(statement).all()

    return {"data": clients, "count": count}
