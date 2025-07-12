import pytest
from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient
from pydantic import ValidationError, BaseModel, Field

from app.api.errors.handlers import http_exception_handler, validation_exception_handler

class _TestModel(BaseModel):
    __test__ = False
    required_field: str = Field(...)

@pytest.fixture(scope="module")
def app_with_handlers():
    app = FastAPI()
    app.exception_handler(HTTPException)(http_exception_handler)
    app.exception_handler(ValidationError)(validation_exception_handler)

    @app.get("/test-http-exception")
    async def test_http_exception():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    @app.post("/test-validation-error")
    async def test_validation_error_endpoint(data: _TestModel):
        return {"message": "success"}

    return app

@pytest.fixture(scope="module")
def client_with_handlers(app_with_handlers: FastAPI):
    return TestClient(app_with_handlers)

def test_http_exception_handler(client_with_handlers: TestClient):
    response = client_with_handlers.get("/test-http-exception")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Item not found"}

def test_validation_exception_handler(client_with_handlers: TestClient):
    response = client_with_handlers.post("/test-validation-error", json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "detail" in response.json()
    assert len(response.json()["detail"]) > 0
    assert response.json()["detail"][0]["loc"] == ["body", "required_field"]
    assert response.json()["detail"][0]["msg"] == "Field required"
    assert response.json()["detail"][0]["type"] == "missing"
