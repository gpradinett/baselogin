from typing import Any
from sqlmodel import Session
from app.models import User, UserCreate, UserUpdate
from app.crud import user as crud_user
from app.core.security import get_password_hash, verify_password
import uuid

class UserService:
    def __init__(self, session: Session):
        self.session = session

    def create_user(self, user_in: UserCreate) -> User:
        hashed_password = get_password_hash(user_in.password)
        user_data = user_in.model_dump()
        user_data["hashed_password"] = hashed_password
        user_data.pop("password")
        db_obj = User(**user_data)
        return crud_user.create_user(session=self.session, user=db_obj)

    def update_user(self, user_id: uuid.UUID, user_in: UserUpdate) -> User:
        db_user = crud_user.get_user_by_id(session=self.session, user_id=user_id)
        if not db_user:
            raise ValueError("User not found")
        
        user_data = user_in.model_dump(exclude_unset=True)
        if "password" in user_data:
            hashed_password = get_password_hash(user_data["password"])
            user_data["hashed_password"] = hashed_password
            user_data.pop("password")
        
        return crud_user.update_user(session=self.session, db_user=db_user, user_data=user_data)

    def authenticate(self, email: str, password: str) -> User | None:
        user = crud_user.get_user_by_email(session=self.session, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
