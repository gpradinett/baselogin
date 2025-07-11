from uuid import UUID
from fastapi import HTTPException
from sqlmodel import Session
from app.crud import user as crud_user
from app import models
from app.core.config import settings
from app.utils.email_utils import generate_new_account_email, send_email
from app.models import User


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_in: models.UserCreate) -> models.User:
        user = crud_user.get_user_by_email(session=self.db, email=user_in.email)
        if user:
            raise HTTPException(
                status_code=400,
                detail="The user with this email already exists in the system.",
            )
        new_user = crud_user.create_user(session=self.db, user_create=user_in)
        
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
        user_to_delete = crud_user.get_user_by_id(session=self.db, user_id=user_id)
        
        if not user_to_delete:
            raise HTTPException(status_code=404, detail="The user with this username does not exist in the system.")

        if current_user.id == user_to_delete.id:
            raise HTTPException(
                status_code=400, 
                detail="Superusers can't delete themselves."
            )

        crud_user.delete_user(session=self.db, user=user_to_delete)
        return user_to_delete

    def update_user(self, user_id: UUID, user_in: models.UserUpdate) -> models.User:
        user_to_update = crud_user.get_user_by_id(session=self.db, user_id=user_id)
        if not user_to_update:
            raise HTTPException(
                status_code=404,
                detail="The user with this username does not exist in the system.",
            )

        if user_in.email:
            existing_user = crud_user.get_user_by_email(session=self.db, email=user_in.email)
            if existing_user and existing_user.id != user_to_update.id:
                raise HTTPException(
                    status_code=400,
                    detail="The user with this email already exists in the system.",
                )
        
        return crud_user.update_user(session=self.db, db_user=user_to_update, user_in=user_in)

    def delete_user_me(self, current_user: models.User) -> models.Message:
        if current_user.is_superuser:
            raise HTTPException(
                status_code=400, detail="Superusers can't delete themselves."
            )
        crud_user.delete_user(session=self.db, user=current_user)
        return models.Message(message="User deleted successfully")



    def update_user_me(self, user_in: models.UserUpdate, current_user: models.User) -> models.User:
        if user_in.email:
            existing_user = crud_user.get_user_by_email(session=self.db, email=user_in.email)
            if existing_user and existing_user.id != current_user.id:
                raise HTTPException(
                    status_code=400,
                    detail="The user with this email already exists in the system.",
                )
        
        return crud_user.update_user(session=self.db, db_user=current_user, user_in=user_in)