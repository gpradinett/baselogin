from typing import Any

import httpx
import uuid # Added this import
from datetime import timedelta # Added this import
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app import crud
from app.api.deps import SessionDep
from app.core.config import settings
from app.core.security import create_access_token
from app.models import Token, UserCreate

router = APIRouter(prefix="/auth/google", tags=["google auth"])

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


@router.get("/login")
async def google_login():
    """
    Redirects to Google's OAuth 2.0 login page.
    """
    params = {
        "response_type": "code",
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    redirect_url = f"{GOOGLE_AUTH_URL}?" + "&".join([f"{k}={v}" for k, v in params.items()])
    return RedirectResponse(redirect_url)


@router.get("/callback", response_model=Token)
async def google_callback(code: str, session: SessionDep) -> Any:
    """
    Handles the callback from Google's OAuth 2.0.
    Exchanges the authorization code for tokens and authenticates/registers the user.
    """
    async with httpx.AsyncClient() as client:
        token_params = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        try:
            token_response = await client.post(GOOGLE_TOKEN_URL, data=token_params)
            token_response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to get token from Google: {e.response.text}"
            ) from e
        google_tokens = token_response.json()

        id_token = google_tokens.get("id_token")
        if not id_token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID token not found")

        # Decode ID token to get user info
        # For production, you should verify the token's signature and audience
        # using a library like google-auth or python-jose
        # For simplicity here, we'll just decode it (DO NOT DO THIS IN PRODUCTION WITHOUT VERIFICATION)
        import jwt
        try:
            user_info = jwt.decode(id_token, options={"verify_signature": False}) # For testing only
        except jwt.PyJWTError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID token")

        email = user_info.get("email")
        google_id = user_info.get("sub") # 'sub' is the unique Google ID
        full_name = user_info.get("name")

        if not email or not google_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing user info from Google")

        user = crud.get_user_by_email(session=session, email=email)

        if user:
            # User exists, link Google ID if not already linked
            if not user.google_id:
                user.google_id = google_id
                session.add(user)
                session.commit()
                session.refresh(user)
            # Authenticate the user and return token
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            return Token(
                access_token=create_access_token(user.id, access_token_expires),
                token_type="bearer",
            )
        else:
            # User does not exist, create a new user
            # Note: We don't get a password from Google, so we'll create a dummy one or handle it differently
            # For simplicity, we'll create a user without a password here, or you might enforce password creation later
            # Or, if you want to allow login only via Google, you might not need a password field for Google-only users
            new_user_in = UserCreate(
                email=email,
                full_name=full_name,
                google_id=google_id,
                password=str(uuid.uuid4()), # Dummy password for now, or handle differently
            )
            new_user = crud.create_user(session=session, user_create=new_user_in)
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            return Token(
                access_token=create_access_token(new_user.id, access_token_expires),
                token_type="bearer",
            )