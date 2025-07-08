from fastapi import APIRouter

from app.api.routes import users, login, password_reset, clients


api_router = APIRouter()

api_router.include_router(users.router)
api_router.include_router(login.router)
api_router.include_router(password_reset.router, prefix="/password-reset")
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
