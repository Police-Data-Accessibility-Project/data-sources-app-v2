from http import HTTPStatus
from unittest.mock import MagicMock

from database_client.database_client import DatabaseClient
from middleware.login_queries import (
    is_admin,
    generate_api_key,
    get_api_key_for_user,
)



def test_is_admin_happy_path() -> None:
    """
    Creates and inserts two users, one an admin and the other not
    And then checks to see if the `is_admin` properly
    identifies both
    :param db_cursor:
    """
    mock_db_client = MagicMock()
    mock_get_role_by_email_result = MagicMock()
    mock_get_role_by_email_result.role = "admin"
    mock_db_client.get_role_by_email.return_value = mock_get_role_by_email_result

    result = is_admin(mock_db_client, "test_email")
    assert result is True
    mock_db_client.get_role_by_email.assert_called_once_with("test_email")


def test_is_admin_not_admin() -> None:
    """
    Creates and inserts two users, one an admin and the other not
    And then checks to see if the `is_admin` properly
    identifies both
    :param db_cursor:
    """
    mock_db_client = MagicMock()
    mock_get_role_by_email_result = MagicMock()
    mock_get_role_by_email_result.role = "user"
    mock_db_client.get_role_by_email.return_value = mock_get_role_by_email_result

    result = is_admin(mock_db_client, "test_email")
    assert result is False
    mock_db_client.get_role_by_email.assert_called_once_with("test_email")


def test_generate_api_key():
    api_key = generate_api_key()
    assert len(api_key) == 32
    assert all(c in "0123456789abcdef" for c in api_key)


def test_get_api_key_for_user_success(monkeypatch):
    (
        mock_check_password_hash,
        mock_db_client,
        mock_email,
        mock_generate_api_key,
        mock_make_response,
        mock_password,
        mock_password_digest,
        mock_update_api_key,
        mock_user_id,
    ) = setup_mocks(monkeypatch)
    mock_check_password_hash.return_value = True
    mock_api_key = MagicMock()
    mock_generate_api_key.return_value = mock_api_key

    # Call function
    get_api_key_for_user(mock_db_client, mock_email, mock_password)

    mock_db_client.get_user_info.assert_called_with(mock_email)
    mock_check_password_hash.assert_called_with(mock_password_digest, mock_password)
    mock_generate_api_key.assert_called()
    mock_db_client.update_user_api_key.assert_called_with(
        user_id=mock_user_id, api_key=mock_api_key
    )
    mock_make_response.assert_called_with({"api_key": mock_api_key}, HTTPStatus.OK)


def test_get_api_key_for_user_failure(monkeypatch):
    (
        mock_check_password_hash,
        mock_db_client,
        mock_email,
        mock_generate_api_key,
        mock_make_response,
        mock_password,
        mock_password_digest,
        mock_update_api_key,
        mock_user_id,
    ) = setup_mocks(monkeypatch)

    mock_check_password_hash.return_value = False

    get_api_key_for_user(mock_db_client, mock_email, mock_password)

    mock_db_client.get_user_info.assert_called_with(mock_email)
    mock_check_password_hash.assert_called_with(mock_password_digest, mock_password)
    mock_generate_api_key.assert_not_called()
    mock_db_client.update_user_api_key.assert_not_called()
    mock_make_response.assert_called_with(
        {"message": "Invalid email or password"}, HTTPStatus.UNAUTHORIZED
    )


def setup_mocks(monkeypatch):
    mock_db_client = MagicMock()
    mock_email = MagicMock()
    mock_password = MagicMock()
    mock_password_digest = MagicMock()
    mock_user_id = 123
    mock_user_data = DatabaseClient.UserInfo(
        id=mock_user_id,
        password_digest=mock_password_digest,
        api_key=None,
    )
    mock_db_client.get_user_info.return_value = mock_user_data
    mock_check_password_hash = MagicMock()
    mock_api_key = MagicMock()
    mock_generate_api_key = MagicMock(return_value=mock_api_key)
    mock_update_api_key = MagicMock()
    mock_make_response = MagicMock()
    monkeypatch.setattr(
        "middleware.login_queries.check_password_hash", mock_check_password_hash
    )
    monkeypatch.setattr(
        "middleware.login_queries.generate_api_key", mock_generate_api_key
    )
    monkeypatch.setattr("middleware.login_queries.make_response", mock_make_response)
    return (
        mock_check_password_hash,
        mock_db_client,
        mock_email,
        mock_generate_api_key,
        mock_make_response,
        mock_password,
        mock_password_digest,
        mock_update_api_key,
        mock_user_id,
    )
