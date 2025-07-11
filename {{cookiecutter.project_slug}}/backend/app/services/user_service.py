from uuid import UUID
from fastapi import HTTPException
from sqlmodel import Session
from app.crud import user as crud_user
from app import models
from app.core.config import settings
from app.utils.email_utils import generate_new_account_email, send_email
from app.models import User
from app.core.security import get_password_hash, verify_password # Nueva importación


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
        # Hashear la contraseña aquí
        hashed_password = get_password_hash(user_in.password)
        user_data = user_in.model_dump()
        user_data["hashed_password"] = hashed_password
        user_data.pop("password") # Eliminar la contraseña en texto plano

        # Crear un objeto User directamente para pasar al CRUD
        db_obj = models.User(**user_data)
        new_user = crud_user.create_user(session=self.db, user=db_obj) # Cambiar user_create a user
        
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

        user_data = user_in.model_dump(exclude_unset=True)

        if user_data.get("email"):
            existing_user = crud_user.get_user_by_email(session=self.db, email=user_data["email"])
            if existing_user and existing_user.id != user_to_update.id:
                raise HTTPException(
                    status_code=400,
                    detail="The user with this email already exists in the system.",
                )
        
        if "password" in user_data and user_data["password"] is not None:
            hashed_password = get_password_hash(user_data["password"])
            user_data["hashed_password"] = hashed_password
            user_data.pop("password")

        return crud_user.update_user(session=self.db, db_user=user_to_update, user_data=user_data)

    def delete_user_me(self, current_user: models.User) -> models.Message:
        if current_user.is_superuser:
            raise HTTPException(
                status_code=400, detail="Superusers can't delete themselves."
            )
        crud_user.delete_user(session=self.db, user=current_user)
        return models.Message(message="User deleted successfully")



    def update_user_me(self, user_in: models.UserUpdate, current_user: models.User) -> models.User:
        user_data = user_in.model_dump(exclude_unset=True)
        if user_data.get("email"):
            existing_user = crud_user.get_user_by_email(session=self.db, email=user_data["email"])
            if existing_user and existing_user.id != current_user.id:
                raise HTTPException(
                    status_code=400,
                    detail="The user with this email already exists in the system.",
                )
        if "password" in user_data and user_data["password"] is not None:
            hashed_password = get_password_hash(user_data["password"])
            user_data["hashed_password"] = hashed_password
            user_data.pop("password")
        
        return crud_user.update_user(session=self.db, db_user=current_user, user_data=user_data)

    def authenticate(self, email: str, password: str) -> User | None:
        db_user = crud_user.get_user_by_email(session=self.db, email=email)
        if not db_user:
            return None
        if not verify_password(password, db_user.hashed_password):
            return None
        return db_user