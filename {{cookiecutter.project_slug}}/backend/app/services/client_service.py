from typing import Any
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session

from app.crud import client as crud_client
from app.models import Client, ClientCreate, ClientUpdate, ClientCreateResponse


class ClientService:
    def __init__(self, db: Session):
        self.db = db

    def create_client(self, client_in: ClientCreate, owner_id: UUID) -> ClientCreateResponse:
        db_client, client_secret = crud_client.create_client(session=self.db, client_create=client_in, owner_id=owner_id)
        return ClientCreateResponse(client_secret=client_secret, **db_client.model_dump())


    def get_client(self, client_id: str) -> Client:
        return crud_client.get_client_by_client_id(session=self.db, client_id=client_id)

    def update_client(self, client_id: str, client_in: ClientUpdate) -> Client:
        db_client = crud_client.get_client_by_client_id(session=self.db, client_id=client_id)
        return crud_client.update_client(session=self.db, db_client=db_client, client_in=client_in)

    def delete_client(self, client_id: str) -> None:
        db_client = crud_client.get_client_by_client_id(session=self.db, client_id=client_id)
        crud_client.delete_client(session=self.db, db_client=db_client)

    def get_multiple_clients(self, skip: int, limit: int) -> dict[str, Any]:
        return crud_client.get_multiple_clients(session=self.db, skip=skip, limit=limit)