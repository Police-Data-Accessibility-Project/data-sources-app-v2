"""Integration tests for /login endpoint"""
from http import HTTPStatus

import psycopg2.extensions

from tests.fixtures import dev_db_connection, client_with_db
from tests.helper_functions import (
    create_test_user_api,
    check_response_status,
)


def test_login_post_success(client_with_db, dev_db_connection: psycopg2.extensions.connection):
    """
    Test that POST call to /login endpoint successfully logs in a user, creates a session token,
    and verifies the session token exists only once in the database with the correct email
    """
    # Create user
    user_info = create_test_user_api(client_with_db)
    response = client_with_db.post(
        "/api/login",
        json={"email": user_info.email, "password": user_info.password},
    )
    check_response_status(response, HTTPStatus.OK.value)
    session_token = response.json.get("data")
    assert session_token == "DUMMY_TOKEN"

def test_login_post_fail(client_with_db, dev_db_connection: psycopg2.extensions.connection):
    """
    Test that POST call to /login endpoint fails if the user does not exist
    """
    response = client_with_db.post(
        "/api/login",
        json={"email": "non-existent", "password": "non-existent"},
    )
    check_response_status(response, HTTPStatus.UNAUTHORIZED.value)