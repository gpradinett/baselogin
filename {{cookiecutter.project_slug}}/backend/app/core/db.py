from sqlmodel import Session, create_engine, SQLModel

from app.core.config import settings


engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
print(f"Connecting to database: {settings.SQLALCHEMY_DATABASE_URI}")


def init_db(session: Session) -> None:
    """Create the database tables."""
    # Crear todas las tablas si no existen
    SQLModel.metadata.create_all(engine)
    # Crear el primer superusuario si no existe
