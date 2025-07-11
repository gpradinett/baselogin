from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.core.db import init_db


def get_superuser_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    init_db(db)
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers