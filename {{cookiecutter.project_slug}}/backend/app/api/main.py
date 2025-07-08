from fastapi import APIRouter

from app.api.routes import users, login, password_reset, clients, google_auth


api_router = APIRouter()

api_router.include_router(users.router)
api_router.include_router(login.router)
api_router.include_router(password_reset.router, prefix="/password-reset")
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(google_auth.router, prefix="/auth/google", tags=["auth", "google"])
print(f"Registered routes: {[route.path for route in api_router.routes]}")
print("Google Auth router included.")
