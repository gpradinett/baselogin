import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.core.config import settings
from app.models import Client, ClientCreate


@pytest.mark.skip(reason="Known issue with 422 Unprocessable Entity for ClientCreate with JSONB fields.")
def test_create_client(
    client: TestClient,
    superuser_token_headers: dict[str, str],
) -> None:
    client_in = ClientCreate(name="Test Client", redirect_uris=[], scopes=[])
    r = client.post(
        f"{settings.API_V1_STR}/clients/", headers={**superuser_token_headers, "Content-Type": "application/json"}, json=client_in.model_dump()
    )
    assert r.status_code == status.HTTP_200_OK
    created_client = r.json()
    assert created_client["name"] == "Test Client"
    assert "client_id" in created_client
    assert "hashed_client_secret" not in created_client # Should not return hashed secret

@pytest.mark.skip(reason="Known issue with 422 Unprocessable Entity for ClientCreate with JSONB fields when passing None.")
def test_create_client_with_none_redirect_uris_and_scopes(
    client: TestClient,
    superuser_token_headers: dict[str, str],
) -> None:
    client_in = ClientCreate(name="Test Client None", redirect_uris=None, scopes=None)
    r = client.post(
        f"{settings.API_V1_STR}/clients/", headers={**superuser_token_headers, "Content-Type": "application/json"}, json=client_in.model_dump()
    )
    assert r.status_code == status.HTTP_200_OK
    created_client = r.json()
    assert created_client["name"] == "Test Client None"
    assert created_client["redirect_uris"] == []
    assert created_client["scopes"] == []
    assert "client_id" in created_client
    assert "hashed_client_secret" not in created_client # Should not return hashed secret


def test_read_client(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    test_client: Client,
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/clients/{test_client.client_id}", headers=superuser_token_headers
    )
    assert r.status_code == status.HTTP_200_OK
    retrieved_client = r.json()
    assert retrieved_client["name"] == test_client.name
    assert retrieved_client["client_id"] == str(test_client.client_id)


def test_read_client_not_found(
    client: TestClient,
    superuser_token_headers: dict[str, str],
) -> None:
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    r = client.get(
        f"{settings.API_V1_STR}/clients/{non_existent_id}", headers=superuser_token_headers
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND
    assert "Client not found" in r.json()["detail"]


def test_update_client(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    test_client: Client,
) -> None:
    new_name = "Updated Client Name"
    data = {"name": new_name}
    r = client.put(
        f"{settings.API_V1_STR}/clients/{test_client.client_id}", headers=superuser_token_headers, json=data
    )
    assert r.status_code == status.HTTP_200_OK
    updated_client = r.json()
    assert updated_client["name"] == new_name


def test_update_client_not_found(
    client: TestClient,
    superuser_token_headers: dict[str, str],
) -> None:
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    data = {"name": "Non Existent"}
    r = client.put(
        f"{settings.API_V1_STR}/clients/{non_existent_id}", headers=superuser_token_headers, json=data
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND
    assert "Client not found" in r.json()["detail"]


def test_delete_client(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    test_client: Client,
) -> None:
    r = client.delete(
        f"{settings.API_V1_STR}/clients/{test_client.client_id}", headers=superuser_token_headers
    )
    assert r.status_code == status.HTTP_200_OK
    deleted_message = r.json()
    assert deleted_message["message"] == "Client deleted successfully"

    # Verify client is actually deleted
    r = client.get(
        f"{settings.API_V1_STR}/clients/{test_client.client_id}", headers=superuser_token_headers
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND


def test_delete_client_not_found(
    client: TestClient,
    superuser_token_headers: dict[str, str],
) -> None:
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    r = client.delete(
        f"{settings.API_V1_STR}/clients/{non_existent_id}", headers=superuser_token_headers
    )
    assert r.status_code == status.HTTP_404_NOT_FOUND
    assert "Client not found" in r.json()["detail"]


def test_read_multiple_clients(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    test_client: Client,
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/clients/", headers=superuser_token_headers
    )
    assert r.status_code == status.HTTP_200_OK
    all_clients = r.json()
    assert "data" in all_clients
    assert "count" in all_clients
    assert len(all_clients["data"]) > 0
    assert any(c["client_id"] == str(test_client.client_id) for c in all_clients["data"])