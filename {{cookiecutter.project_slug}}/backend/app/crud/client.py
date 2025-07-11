import uuid
from typing import Any
from uuid import UUID
from fastapi import HTTPException

from sqlmodel import Session, select
from sqlalchemy import func

from app.core.security import get_password_hash
from app.models import Client, ClientCreate, ClientUpdate


def create_client(*, session: Session, client_create: ClientCreate, owner_id: UUID) -> Client:
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
    db_obj = Client(
        name=client_create.name,
        redirect_uris=client_create.redirect_uris or [],
        scopes=client_create.scopes or [],
        is_active=client_create.is_active,
        hashed_client_secret=get_password_hash(client_secret),
        owner_id=owner_id,
    )
    print(f"db_obj before add: {db_obj.model_dump_json()}")
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    # Return the client object along with the unhashed client_secret
    # The unhashed secret should only be returned once upon creation
    return db_obj, client_secret


def get_client_by_client_id(*, session: Session, client_id: str) -> Client:
    """
    Retrieves a client by its client_id.

    Args:
        session: The database session.
        client_id: The client_id of the client to retrieve.

    Returns:
        The Client object if found.

    Raises:
        HTTPException: If the client is not found.
    """
    statement = select(Client).where(Client.client_id == client_id)
    session_client = session.exec(statement).first()
    if not session_client:
        raise HTTPException(status_code=404, detail="Client not found")
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
