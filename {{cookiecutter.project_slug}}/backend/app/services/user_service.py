from typing import Any
from uuid import UUID
from fastapi import HTTPException
from sqlmodel import Session
from app.crud import user as crud_user
from app import models
from app.core.config import settings
from app.utils.email_utils import generate_new_account_email, send_email
from app.models import User
from app.core.security import get_password_hash, verify_password


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_in: models.UserCreate) -> models.User:
        self._validate_email_uniqueness(user_in.email)
        
        hashed_password = get_password_hash(user_in.password)
        user_data = user_in.model_dump()
        user_data["hashed_password"] = hashed_password
        user_data.pop("password") # Remove plaintext password

        # Create a User object directly to pass to CRUD
        db_obj = models.User(**user_data)
        new_user = crud_user.create_user(session=self.db, user=db_obj) # Change user_create to user
        
        if settings.emails_enabled and user_in.email:
            email_data = generate_new_account_email(
                email_to=user_in.email, username=user_in.email, password=user_in.password
            )
            send_email(
                email_to=user_in.email,
                email_data=email_data,
            )
        return new_user


    def delete_user(self, user_id: UUID, current_user: models.User) -> models.User:
        user_to_delete = self._get_user_or_raise_not_found(user_id)
        
        if current_user.id == user_to_delete.id:
            self._raise_cannot_delete_self()

        crud_user.delete_user(session=self.db, user=user_to_delete)
        return user_to_delete

    def update_user(self, user_id: UUID, user_in: models.UserUpdate) -> models.User:
        user_to_update = self._get_user_or_raise_not_found(user_id)

        user_data = user_in.model_dump(exclude_unset=True)

        if user_data.get("email"):
            self._validate_email_uniqueness(user_data["email"], user_to_update.id)
        
        self._process_password(user_data)

        return crud_user.update_user(session=self.db, db_user=user_to_update, user_data=user_data)

    def delete_user_me(self, current_user: models.User) -> models.Message:
        if current_user.is_superuser:
            self._raise_cannot_delete_self()
        crud_user.delete_user(session=self.db, user=current_user)
        return models.Message(message="User deleted successfully")



    def update_user_me(self, user_in: models.UserUpdate, current_user: models.User) -> models.User:
        user_data = user_in.model_dump(exclude_unset=True)
        if user_data.get("email"):
            self._validate_email_uniqueness(user_data["email"], current_user.id)
        self._process_password(user_data)
        
        return crud_user.update_user(session=self.db, db_user=current_user, user_data=user_data)

    def authenticate(self, email: str, password: str) -> User | None:
        db_user = crud_user.get_user_by_email(session=self.db, email=email)
        if not db_user:
            return None
        if not verify_password(password, db_user.hashed_password):
            return None
        return db_user


    def get_multiple_users(self, skip: int, limit: int) -> dict[str, Any]:                  
        return crud_user.get_multiple_users(session=self.db, skip=skip, limit=limit)
    
    def _raise_user_not_found(self):
        raise HTTPException(status_code=404, detail="The user with this username does not exist in the system.")

    def _raise_email_already_exists(self):
        raise HTTPException(status_code=400, detail="The user with this email already exists in the system.")

    def _raise_cannot_delete_self(self):
        raise HTTPException(status_code=400, detail="Superusers can't delete themselves.")

    def _get_user_or_raise_not_found(self, user_id: UUID) -> models.User:
        user = crud_user.get_user_by_id(session=self.db, user_id=user_id)
        if not user:
            self._raise_user_not_found()
        return user

    def _validate_email_uniqueness(self, email: str, current_user_id: UUID | None = None):
        existing_user = crud_user.get_user_by_email(session=self.db, email=email)
        if existing_user and (current_user_id is None or existing_user.id != current_user_id):
            self._raise_email_already_exists()

    def _process_password(self, user_data: dict):
        if "password" in user_data and user_data["password"] is not None:
            hashed_password = get_password_hash(user_data["password"])
            user_data["hashed_password"] = hashed_password
            user_data.pop("password")

    def _validate_email_uniqueness(self, email: str, current_user_id: UUID | None = None):
        existing_user = crud_user.get_user_by_email(session=self.db, email=email)
        if existing_user and (current_user_id is None or existing_user.id != current_user_id):
            self._raise_email_already_exists()

    def _process_password(self, user_data: dict):
        if "password" in user_data and user_data["password"] is not None:
            hashed_password = get_password_hash(user_data["password"])
            user_data["hashed_password"] = hashed_password
            user_data.pop("password")