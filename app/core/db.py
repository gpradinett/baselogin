from sqlmodel import Session, create_engine, select, SQLModel

from app import crud
from app.core.config import settings
from app.models import User, UserCreate


engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
print(f"Connecting to database: {settings.SQLALCHEMY_DATABASE_URI}")

def init_db(session: Session) -> None:
    """Create the database tables."""
    # Crear todas las tablas si no existen
    SQLModel.metadata.create_all(engine)
    # Crear el primer superusuario si no existe
    