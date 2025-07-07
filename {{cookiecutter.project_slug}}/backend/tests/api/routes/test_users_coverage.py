from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from tests.utils.user import create_random_user
from tests.factories import UserCreateFactory, UserUpdateFactory, faker


def test_update_user_email_conflict(
    client: TestClient, db: Session, superuser_token_headers: dict[str, str]
) -> None:
    """
    Test updating a user's email to one that already exists for another user.
    """
    # Create two users
    user1, _ = create_random_user(db)
    user2, _ = create_random_user(db)

    # Try to update user1's email to user2's email
    user_update_in = UserUpdateFactory.build(email=user2.email)
    response = client.patch(
        f"{settings.API_V1_STR}/users/{user1.id}",
        headers={**superuser_token_headers, 'Content-Type': 'application/json'},
        content=user_update_in.model_dump_json()
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "The user with this email already exists in the system."}


def test_create_user_email_sending_enabled(client: TestClient, db: Session) -> None:
    """
    Test that email sending logic is covered when emails are enabled.
    This test will require mocking the send_email and generate_new_account_email functions.
    """
    # Mock the email sending functions and settings.emails_enabled
    import app.utils
    import app.core.config
    from unittest.mock import patch, PropertyMock

    with patch.object(app.api.routes.users, 'send_email') as mock_send_email,          patch.object(app.api.routes.users, 'generate_new_account_email') as mock_generate_email,          patch.object(app.api.routes.users, 'settings') as mock_settings,          patch.object(app.crud, 'get_user_by_email', return_value=None) as mock_get_user_by_email:

        mock_settings.emails_enabled = True
        mock_generate_email.return_value = {"subject": "Test", "body": "Test"}

        user_in = UserCreateFactory.build(email=faker.unique.email())
        response = client.post(
            f"{settings.API_V1_STR}/users/",
            content=user_in.model_dump_json(),
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 200
        mock_send_email.assert_called_once()
        mock_generate_email.assert_called_once()
