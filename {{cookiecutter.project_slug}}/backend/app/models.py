import uuid
from datetime import datetime, timezone
from typing import List # Added this import
from pydantic import EmailStr
from sqlmodel import Field, SQLModel
import sqlalchemy as sa # Added this import


# shared properties
class UserBase(SQLModel):
    email: EmailStr | None = Field(default=None, unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    name: str | None = Field(default=None, max_length=255)
    last_name: str | None = Field(default=None, max_length=255)
    cellphone: int | None = Field(default=None)
    has_mfa: bool = False
    create_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Database model, database table inferred from class name
class User(UserBase, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str | None = Field(default=None, max_length=255)
    password_reset_token: str | None = Field(default=None, index=True)
    password_reset_token_expires: datetime | None = Field(default=None)
    google_id: str | None = Field(default=None, unique=True, index=True) # Added for Google OAuth


# Shared properties for Client
class ClientBase(SQLModel):
    """
    Base class for Client models, defining common properties.
    Represents an application or service that interacts with the authentication system.
    """
    name: str = Field(index=True, max_length=255)
    redirect_uris: List[str] = Field(default_factory=list, sa_column=sa.Column(sa.JSON))
    scopes: List[str] = Field(default_factory=list, sa_column=sa.Column(sa.JSON))
    is_active: bool = True


# Database model for Client
class Client(ClientBase, table=True):
    """
    Database model for Client applications.
    Stores client credentials (client_id, client_secret) and related information.
    """
    __tablename__ = "clients"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    client_id: uuid.UUID = Field(default_factory=uuid.uuid4, unique=True, index=True)
    hashed_client_secret: str = Field(max_length=255)
    owner_id: uuid.UUID = Field(default=None, foreign_key="users.id")


# Properties to receive via API on creation
class ClientCreate(ClientBase):
    """
    Properties to receive via API when creating a new Client.
    Inherits all fields from ClientBase.
    """
    pass


# Properties to return via API, id and client_id are always required
class ClientPublic(ClientBase):
    """
    Properties to return via API for a Client.
    Includes id and client_id, but excludes sensitive information like hashed_client_secret.
    """
    id: uuid.UUID
    client_id: uuid.UUID


class ClientCreateResponse(ClientPublic):
    """
    Response model for client creation, includes the unhashed client_secret.
    """
    client_secret: str


# Properties to receive via API on update, all are optional
class ClientUpdate(ClientBase):
    """
    Properties to receive via API when updating an existing Client.
    All fields are optional, allowing partial updates.
    """
    name: str | None = Field(default=None, max_length=255)
    redirect_uris: List[str] | None = Field(default=None)
    scopes: List[str] | None = Field(default=None)
    is_active: bool | None = Field(default=None)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)
    google_id: str | None = None


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)
    password_reset_token: str | None = None
    password_reset_token_expires: datetime | None = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)
    name: str | None = Field(default=None, max_length=255)
    last_name : str | None = Field(default=None, max_length=255)


# Generate Message
class Message(SQLModel):
    message: str


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class ResetPassword(SQLModel):
    token: str
    new_password: str
