from typing import Any
import uuid
from fastapi import HTTPException

from sqlmodel import Session, select
from sqlalchemy import func

from app.core.security import get_password_hash, verify_password
from app.models import User, UserCreate, UserUpdate


def create_user(*, session: Session, user: User) -> User:
    """
    Crea un nuevo usuario en la base de datos.

    Args:
        session: La sesión de la base de datos.
        user: El objeto User a crear.

    Returns:
        El objeto User creado.
    """
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def update_user(*, session: Session, db_user: User, user_data: dict[str, Any]) -> User:
    """
    Actualiza un usuario existente en la base de datos.

    Args:
        session: La sesión de la base de datos.
        db_user: El objeto User existente a actualizar.
        user_data: Un diccionario con los datos a actualizar.

    Returns:
        El objeto User actualizado.
    """
    db_user.sqlmodel_update(user_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_id(*, session: Session, user_id: uuid.UUID) -> User | None:
    """
    Obtiene un usuario por su ID.

    Args:
        session: La sesión de la base de datos.
        user_id: El ID del usuario.

    Returns:
        El objeto User si se encuentra, de lo contrario None.
    """
    return session.get(User, user_id)


def get_user_by_email(*, session: Session, email: str) -> User | None:
    """
    Obtiene un usuario por su dirección de correo electrónico.

    Args:
        session: La sesión de la base de datos.
        email: La dirección de correo electrónico del usuario.

    Returns:
        El objeto User si se encuentra, de lo contrario None.
    """
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def get_multiple_users(*, session: Session, skip: int, limit: int) -> dict[str, Any]:
    """
    Obtiene múltiples usuarios con paginación.

    Args:
        session: La sesión de la base de datos.
        skip: El número de registros a omitir.
        limit: El número máximo de registros a devolver.

    Returns:
        Un diccionario con la lista de usuarios y el conteo total.
    """
    count_statement = select(func.count()).select_from(User)
    count = session.scalar(count_statement)
    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()
    return {"data": users, "count": count}


def get_user_by_password_reset_token(*, session: Session, token: str) -> User | None:
    """
    Obtiene un usuario por su token de restablecimiento de contraseña.

    Args:
        session: La sesión de la base de datos.
        token: El token de restablecimiento de contraseña.

    Returns:
        El objeto User si se encuentra, de lo contrario None.
    """
    statement = select(User).where(User.password_reset_token == token)
    return session.exec(statement).first()



def delete_user(*, session: Session, user: User) -> None:
    """
    Deletes a user from the database.

    Args:
        session: The database session.
        user: The User object to delete.
    """
    session.delete(user)
    session.commit()