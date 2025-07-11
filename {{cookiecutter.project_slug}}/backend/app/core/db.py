from sqlmodel import Session, create_engine, SQLModel

from app.core.config import settings
from app.models import UserCreate
from app import crud


engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
print(f"Connecting to database: {settings.SQLALCHEMY_DATABASE_URI}")


def init_db(session: Session) -> None:
    """Create the database tables and the first superuser if not exists."""
    
    # 🧱 Create tables if they do not exist
    SQLModel.metadata.create_all(engine)

    user = crud.get_user_by_email(session=session, email=settings.FIRST_SUPERUSER)
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        crud.create_user(session=session, user_create=user_in)