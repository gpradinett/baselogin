from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Body
from sqlmodel import Session

from app.crud import client as crud_client
from app.api.deps import SessionDep, get_current_active_superuser
from app.models import Client, ClientCreate, ClientPublic, ClientUpdate, Message, ClientCreateResponse
from app.services.client_service import ClientService

router = APIRouter(prefix="/clients", tags=["clients"])

def get_client_service(session: Session = Depends(SessionDep)) -> ClientService:
    return ClientService(session)

@router.post("/", response_model=ClientCreateResponse)
def create_client(
    client_in: ClientCreate = Body(...),
    client_service: ClientService = Depends(get_client_service),
    current_user: Client = Depends(get_current_active_superuser),
) -> Any:
    """
    Create new client.
    """
    return client_service.create_client(client_in=client_in, owner_id=current_user.id)


@router.get("/{client_id}", response_model=ClientPublic)
def read_client(
    client_id: UUID,
    session: SessionDep,
    current_user: Client = Depends(get_current_active_superuser),
) -> Any:
    """
    Get client by ID.
    """
    return crud_client.get_client_by_client_id(session=session, client_id=client_id)


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
    client = crud_client.get_client_by_client_id(session=session, client_id=client_id)
    return crud_client.update_client(session=session, db_client=client, client_in=client_in)


@router.delete("/{client_id}", response_model=Message)
def delete_client(
    client_id: UUID,
    session: SessionDep,
    current_user: Client = Depends(get_current_active_superuser),
) -> Any:
    """
    Delete a client.
    """
    client = crud_client.get_client_by_client_id(session=session, client_id=client_id)
    crud_client.delete_client(session=session, db_client=client)
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
    return crud_client.get_multiple_clients(session=session, skip=skip, limit=limit)