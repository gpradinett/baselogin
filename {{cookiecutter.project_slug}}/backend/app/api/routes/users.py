import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.core.config import settings

from app.utils import generate_new_account_email, send_email

from app import crud
from app.api.deps import (
    CurrentUser,
    SessionDep,
)
from app.api.deps import get_current_active_superuser as gcau
from app.models import (
    User,
    UserCreate,
    UsersPublic,
    UserPublic,
    Message,
    UserUpdate,
    UserRegister,
)


router = APIRouter(prefix="/users", tags=["users"])


"""
Get all users
"""


@router.get("/", dependencies=[Depends(gcau)], response_model=UsersPublic)
async def read_users(
    *,
    session: SessionDep,  # type: ignore
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get current user.
    """

    users_data = crud.get_multiple_users(session=session, skip=skip, limit=limit)
    return UsersPublic(
        data=users_data["data"],
        count=users_data["count"],
    )


"""
Get current user
"""


@router.get("/me", response_model=UserPublic)
async def read_user_me(
    current_user: CurrentUser,
) -> Any:
    """
    Get current user.
    """
    print("Current user:", current_user)
    return current_user


"""
Create new user
"""


@router.post("/", response_model=UserPublic)
async def create_user(
    *,
    session: SessionDep,  # type: ignore
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = crud.create_user(session=session, user_create=user_in)
    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email,
            username=user_in.email,
            password=user_in.password,
        )
        send_email(
            email_to=user_in.email,
            email_data=email_data,
        )
    print(user)
    return user


"""
Delete user
"""


@router.delete("/me", response_model=Message)
async def delete_user_me(
    current_user: CurrentUser,
    session: SessionDep,  # type: ignore
) -> Any:
    """
    Delete current user.
    """
    if current_user.is_superuser:
        raise HTTPException(
            status_code=400,
            detail="Superuser cannot delete himself.",
        )
    session.delete(current_user)
    session.commit()
    return Message(message="User deleted successfully.")


"""
Update user
"""


@router.patch("/{user_id}", dependencies=[Depends(gcau)], response_model=UserPublic)
async def update_user(
    *,
    session: SessionDep,  # type: ignore
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    """
    Update user by id.
    """
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )
    if user_in.email:
        existing_user = crud.get_user_by_email(
            session=session,
            email=user_in.email,
        )
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=400,
                detail="The user with this email already exists in the system.",
            )
    db_user = crud.update_user(
        session=session,
        db_user=db_user,
        user_in=user_in,
    )
    return db_user


"""
Delete user by id
"""


@router.delete("/{user_id}", dependencies=[Depends(gcau)])
async def delete_user(
    *,
    session: SessionDep,  # type: ignore
    user_id: uuid.UUID,
    current_user: CurrentUser,
) -> Message:
    """
    Delete user by id.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )
    if user == current_user:
        raise HTTPException(
            status_code=403,
            detail="You cannot delete yourself.",
        )
    session.delete(user)
    session.commit()
    return Message(message="User deleted successfully.")


"""
Sign up user
"""


@router.post("/signup", response_model=User)
async def register_user(session: SessionDep, user_in: UserRegister) -> UserPublic:  # type: ignore
    """
    Create new user without the need to be logged in.
    """
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user_create = UserCreate.model_validate(user_in)
    user = crud.create_user(session=session, user_create=user_create)
    return user
