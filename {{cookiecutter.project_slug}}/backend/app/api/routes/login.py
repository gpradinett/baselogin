from datetime import timedelta

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.core import security
from app.api.deps import SessionDep
from app.core.config import settings
from app.models import Token
from app.services.user_service import UserService # Nueva importación

router = APIRouter(tags=["login"])

def get_user_service(session: SessionDep) -> UserService:
    return UserService(session)


@router.post("/login/access-token")
async def login_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],  # type: ignore
    user_service: UserService = Depends(get_user_service), # type: ignore
) -> Token:
    """Login with access token."""
    user = user_service.authenticate(
        email=form_data.username,
        password=form_data.password,
    )
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
    )