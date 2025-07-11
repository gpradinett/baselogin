from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.routing import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from sqlmodel import Session

from app.api.main import api_router
from app.core.db import init_db, engine
from app.core.config import settings
from app.api.errors.handlers import http_exception_handler, validation_exception_handler


def custom_generate_unique_id(route: APIRouter) -> str:
    if route.tags:
        return f"{route.tags[0]}-{route.name}"
    return route.name


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🔹 Logic to initialize the DB at startup
    with Session(engine) as session:
        init_db(session)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
)

app.exception_handler(HTTPException)(http_exception_handler)
app.exception_handler(ValidationError)(validation_exception_handler)


# set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)