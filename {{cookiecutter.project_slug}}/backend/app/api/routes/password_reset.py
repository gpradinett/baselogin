from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import EmailStr

from app.core.config import settings
from app.api.deps import SessionDep
from app.models import Message, ResetPassword
from app.crud import user as crud_user
from app.utils import generate_password_reset_email, send_email
from app.core import security

router = APIRouter(prefix="/password-reset", tags=["login"])


@router.post("/request-password-reset", response_model=Message)
async def request_password_reset(
    email: EmailStr,
    session: SessionDep,  # type: ignore
) -> Any:
    """Request password reset token.
    """
    user = crud_user.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=404, detail="User with this email does not exist."
        )

    password_reset_token = security.generate_password_reset_token(email=email)
    user.password_reset_token = password_reset_token
    user.password_reset_token_expires = security.get_password_reset_token_expire_time()
    session.add(user)
    session.commit()
    session.refresh(user)

    if settings.emails_enabled and user.email:
        email_data = generate_password_reset_email(
            email_to=user.email,
            token=password_reset_token,
        )
        send_email(
            email_to=user.email,
            email_data=email_data,
        )

    return Message(message="Password reset email sent.")


@router.post("/reset-password", response_model=Message)
async def reset_password(
    *,
    session: SessionDep,  # type: ignore
    body: ResetPassword,
) -> Any:
    """Reset password using token.
    """
    user = crud_user.get_user_by_password_reset_token(session=session, token=body.token)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid token.")

    if security.is_password_reset_token_expired(user.password_reset_token_expires):
        raise HTTPException(status_code=400, detail="Token expired.")

    user.hashed_password = security.get_password_hash(body.new_password)
    user.password_reset_token = None
    user.password_reset_token_expires = None
    session.add(user)
    session.commit()
    session.refresh(user)

    return Message(message="Password reset successfully.")
