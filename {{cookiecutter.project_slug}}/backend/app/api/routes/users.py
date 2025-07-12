from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.config import settings
from app.utils.email_utils import generate_new_account_email, send_email
from app.crud import user as crud_user
from app.api import deps
from app import models
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

def get_user_service(db: Session = Depends(deps.get_db)) -> UserService:
    return UserService(db)

@router.get("/", response_model=models.UsersPublic)
def read_users(
    session: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    users_data = crud_user.get_multiple_users(session=session, skip=skip, limit=limit)
    return models.UsersPublic(
        data=users_data["data"],
        count=users_data["count"],
    )

@router.post("/", response_model=models.User)
def create_user(
    *, 
    user_in: models.UserCreate,
    user_service: UserService = Depends(get_user_service),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new user.
    """
    return user_service.create_user(user_in=user_in)

@router.post("/signup", response_model=models.User)
def register_user(user_in: models.UserRegister, user_service: UserService = Depends(get_user_service)) -> Any:
    """
    Create new user without the need to be logged in.
    """
    return user_service.create_user(user_in=models.UserCreate.model_validate(user_in))

@router.get("/me", response_model=models.User)
def read_user_me(current_user: models.User = Depends(deps.get_current_user)) -> Any:
    """
    Get current user.
    """
    return current_user

@router.delete("/me", response_model=models.Message)
def delete_user_me(
    user_service: UserService = Depends(get_user_service),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete own user.
    """
    result = user_service.delete_user_me(current_user=current_user)
    print(result)
    return result

@router.patch("/{user_id}", response_model=models.User)
def update_user(
    user_id: UUID,
    user_in: models.UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> models.User:
    """
    Update a user.
    """
    return user_service.update_user(user_id=user_id, user_in=user_in)

@router.delete("/{user_id}")
def delete_user(
    user_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    user_service: UserService = Depends(get_user_service),
) -> models.User:
    """
    Delete a user.
    """
    return user_service.delete_user(user_id=user_id, current_user=current_user)
