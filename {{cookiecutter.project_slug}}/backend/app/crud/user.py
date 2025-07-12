from typing import Any
import uuid

from sqlmodel import Session, select
from sqlalchemy import func

from app.models import User


def create_user(*, session: Session, user: User) -> User:
    """
    Creates a new user in the database.

    Args:
        session: The database session.
        user: The User object to create.

    Returns:
        The created User object.
    """
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def update_user(*, session: Session, db_user: User, user_data: dict[str, Any]) -> User:
    """
    Updates an existing user in the database.

    Args:
        session: The database session.
        db_user: The existing User object to update.
        user_data: A dictionary with the data to update.

    Returns:
        The updated User object.
    """
    db_user.sqlmodel_update(user_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_id(*, session: Session, user_id: uuid.UUID) -> User | None:
    """
    Retrieves a user by their ID.

    Args:
        session: The database session.
        user_id: The ID of the user.

    Returns:
        The User object if found, otherwise None.
    """
    return session.get(User, user_id)


def get_user_by_email(*, session: Session, email: str) -> User | None:
    """
    Retrieves a user by their email address.

    Args:
        session: The database session.
        email: The email address of the user.

    Returns:
        The User object if found, otherwise None.
    """
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def get_multiple_users(*, session: Session, skip: int, limit: int) -> dict[str, Any]:
    """
    Retrieves multiple users with pagination.

    Args:
        session: The database session.
        skip: The number of records to skip.
        limit: The maximum number of records to return.

    Returns:
        A dictionary with the list of users and the total count.
    """
    count_statement = select(func.count()).select_from(User)
    count = session.scalar(count_statement)
    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()
    return {"data": users, "count": count}


def get_user_by_password_reset_token(*, session: Session, token: str) -> User | None:
    """
    Retrieves a user by their password reset token.

    Args:
        session: The database session.
        token: The password reset token.

    Returns:
        The User object if found, otherwise None.
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