"""Integration tests for /reset-token-validation endpoint."""

from http import HTTPStatus
from pytest_mock import mocker

from tests.helper_functions import (
    create_test_user_api,
    request_reset_password_api,
    check_response_status,
)
from tests.fixtures import dev_db_connection, client_with_db


def test_reset_token_validation(client_with_db, dev_db_connection, mocker):
    """
    Test that POST call to /reset-token-validation endpoint successfully validates the reset token and returns the correct message indicating token validity
    """
    user_info = create_test_user_api(client_with_db)
    token = request_reset_password_api(client_with_db, mocker, user_info)
    response = client_with_db.post("/reset-token-validation", json={"token": token})
    check_response_status(response, HTTPStatus.OK.value)
    assert (
        response.json.get("message") == "Token is valid"
    ), "Message does not return 'Token is valid'"
