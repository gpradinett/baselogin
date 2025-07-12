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
        from app.core.security import get_password_hash
        from app.models import User

        hashed_password = get_password_hash(user_in.password)
        user_data = user_in.model_dump()
        user_data["hashed_password"] = hashed_password
        user_data.pop("password")
        db_obj = User(**user_data)
        crud.create_user(session=session, user=db_obj)