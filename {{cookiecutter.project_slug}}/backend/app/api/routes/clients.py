from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app import crud
from app.api.deps import SessionDep, get_current_active_superuser
from app.models import Client, ClientCreate, ClientPublic, ClientUpdate, Message, ClientCreateResponse

router = APIRouter()


@router.post("/", response_model=ClientCreateResponse)
def create_client(
    client_in: ClientCreate,
    session: SessionDep,
    current_user: Client = Depends(get_current_active_superuser),
) -> Any:
    """
    Create new client.
    """
    db_client, client_secret = crud.create_client(session=session, client_create=client_in, owner_id=current_user.id)
    return ClientCreateResponse(client_secret=client_secret, **db_client.model_dump())


@router.get("/{client_id}", response_model=ClientPublic)
def read_client(
    client_id: UUID,
    session: SessionDep,
    current_user: Client = Depends(get_current_active_superuser),
) -> Any:
    """
    Get client by ID.
    """
    client = crud.get_client_by_client_id(session=session, client_id=client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.put("/{client_id}", response_model=ClientPublic)
def update_client(
    client_id: UUID,
    client_in: ClientUpdate,
    session: SessionDep,
    current_user: Client = Depends(get_current_active_superuser),
) -> Any:
    """
    Update a client.
    """
    client = crud.get_client_by_client_id(session=session, client_id=client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    client = crud.update_client(session=session, db_client=client, client_in=client_in)
    return client


@router.delete("/{client_id}", response_model=Message)
def delete_client(
    client_id: UUID,
    session: SessionDep,
    current_user: Client = Depends(get_current_active_superuser),
) -> Any:
    """
    Delete a client.
    """
    client = crud.get_client_by_client_id(session=session, client_id=client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    crud.delete_client(session=session, db_client=client)
    return {"message": "Client deleted successfully"}


@router.get("/", response_model=dict[str, Any])
def read_clients(
    session: SessionDep,
    current_user: Client = Depends(get_current_active_superuser),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve clients.
    """
    clients = crud.get_multiple_clients(session=session, skip=skip, limit=limit)
    return clients
