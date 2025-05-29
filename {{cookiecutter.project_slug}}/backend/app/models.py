import uuid
from pydantic import EmailStr
from sqlmodel import Field, SQLModel


# shared properties
class UserBase(SQLModel):
    email: EmailStr | None = Field(default=None, unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    """
    name: str | None = Field(default=None, max_length=255)
    last_name: str | None = Field(default=None, max_length=255)
    cellphone: int | None = Field(default=None)
    has_mfa: bool = False
    create_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    """


# Database model, database table inferred from class name
class User(UserBase, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


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
