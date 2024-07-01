import uuid

import pytest

from tests.fixtures import live_database_client, dev_db_connection, db_cursor


def test_add_new_user(live_database_client):
    fake_email = uuid.uuid4().hex
    live_database_client.add_new_user(fake_email, "test_password")
    cursor = live_database_client.cursor
    cursor.execute(f"SELECT password_digest FROM users WHERE email = %s", (fake_email,))
    password_digest = cursor.fetchone()[0]

    assert password_digest == "test_password"


def test_get_user_id(live_database_client):
    # Add a new user to the database
    fake_email = uuid.uuid4().hex
    live_database_client.add_new_user(fake_email, "test_password")

    # Directly fetch the user ID from the database for comparison
    cursor = live_database_client.cursor
    cursor.execute(f"SELECT id FROM users WHERE email = %s", (fake_email,))
    direct_user_id = cursor.fetchone()[0]

    # Get the user ID from the live database
    result_user_id = live_database_client.get_user_id(fake_email)

    # Compare the two user IDs
    assert result_user_id == direct_user_id

def test_set_user_password_digest(live_database_client):
    fake_email = uuid.uuid4().hex
    live_database_client.add_new_user(fake_email, "test_password")
    live_database_client.set_user_password_digest(fake_email, "test_password")
    cursor = live_database_client.cursor
    cursor.execute(f"SELECT password_digest FROM users WHERE email = %s", (fake_email,))
    password_digest = cursor.fetchone()[0]

    assert password_digest == "test_password"

def test_reset_token_logic(live_database_client):
    fake_email = uuid.uuid4().hex
    fake_token = uuid.uuid4().hex
    live_database_client.add_new_user(fake_email, "test_password")
    live_database_client.add_reset_token(fake_email, fake_token)
    reset_token_info = live_database_client.get_reset_token_info(fake_token)
    assert reset_token_info, "Token not found"
    assert reset_token_info.email == fake_email, "Email does not match"

    live_database_client.delete_reset_token(fake_email, fake_token)
    reset_token_info = live_database_client.get_reset_token_info(fake_token)
    assert reset_token_info is None, "Token not deleted"

def test_update_user_api_key(live_database_client):
    # Add a new user to the database

    # Update the user's API key with the DatabaseClint Method

    # Fetch the user's API key from the database to confirm the change

    pytest.fail("Test not implemented")


def test_get_data_source_by_id(live_database_client):
    # Add a new data source and agency to the database

    # Fetch the data source using its id with the DatabaseClient method

    # Confirm the data source and agency are retrieved successfully

    pytest.fail("Test not implemented")


def test_get_approved_data_sources(live_database_client):
    # Add new data sources and agencies to the database, at least two approved and one unapproved

    # Fetch the data sources with the DatabaseClient method

    # Confirm only all approved data sources are retrieved

    pytest.fail("Test not implemented")


def test_get_needs_identification_data_sources(live_database_client):
    # Add new data sources to the database, at least two labeled 'needs identification' and one not

    # Fetch the data sources with the DatabaseClient method

    # Confirm only all data sources labeled 'needs identification' are retrieved

    pytest.fail("Test not implemented")


def test_create_new_data_source_query():
    # Send a data source dictionary to the DatabaseClient method

    # Confirm that the result is the expected query string

    pytest.fail("Test not implemented")


def test_add_new_data_source(live_database_client):
    # Add a new data source to the database with the DatabaseClient method

    # Fetch the data source from the database to confirm that it was added successfully

    pytest.fail("Test not implemented")


def test_update_data_source(live_database_client):
    # Add a new data source to the database

    # Update the data source with the DatabaseClient method

    # Fetch the data source from the database to confirm the change

    pytest.fail("Test not implemented")


def test_create_data_source_update_query(live_database_client):
    # Send a data source dictionary to the DatabaseClient method

    # Confirm that the result is the expected query string

    pytest.fail("Test not implemented")


def test_get_data_sources_for_map(live_database_client):
    # Add at least two new data sources to the database

    # Fetch the data source with the DatabaseClient method

    # Confirm both data sources are retrieved and only the proper columns are returned

    pytest.fail("Test not implemented")


def test_get_agencies_from_page(live_database_client):
    # Add at least two new agencies to the database, if possible add enough to make multiple pages (>1000)

    # Fetch the page of agencies with the DatabaseClient method

    # Confirm that the correct list of agencies is returned for a given page

    pytest.fail("Test not implemented")


def test_get_offset():
    # Send a page number to the DatabaseClient method

    # Confirm that the correct offset is returned

    pytest.fail("Test not implemented")


def test_get_data_sources_to_archive(live_database_client):
    # Add multiple data sources to the database, some that should be archived and some that should not

    # Fetch the data sources using the DatabaseClient method

    # Confirm that only the data sources that should be archived are returned

    pytest.fail("Test not implemented")


def test_update_url_status_to_broken(live_database_client):
    # Add a new data source to the database

    # Update the data source's status with the DatabaseClient method

    # Fetch the data source from the database to confirm the change

    pytest.fail("Test not implemented")


def test_update_last_cached(live_database_client):
    # Add a new data source to the database

    # Update the data source's last_cached value with the DatabaseClient method

    # Fetch the data source from the database to confirm the change

    pytest.fail("Test not implemented")


def test_get_quick_search_results(live_database_client):
    # Add new data sources to the database, some that satisfy the search criteria and some that don't

    # Fetch the search results using the DatabaseClient method

    # Confirm that all data sources that satisfy the search criteria are returned and those that don't are not returned

    pytest.fail("Test not implemented")


def test_add_quick_search_log(live_database_client):
    # Add a quick search log to the database using the DatabaseClient method

    # Fetch the quick search logs to confirm it was added successfully

    pytest.fail("Test not implemented")


def test_add_new_access_token(live_database_client):
    # Call the DatabaseClient method to generate and add a new access token to the database

    # Fetch the new access token from the database to confirm it was added successfully

    pytest.fail("Test not implemented")


def test_get_user_info(live_database_client):
    # Add a new user to the database

    # Fetch the user using its email with the DatabaseClient method

    # Confirm the user is retrieved successfully

    # Attempt to fetch non-existant user

    # Assert UserNotFoundError is raised

    pytest.fail("Test not implemented")


def test_get_role_by_email(live_database_client):
    # Add a new user to the database

    # Fetch the user using its email with the DatabaseClient method

    # Confirm the role is retrieved successfully

    pytest.fail("Test not implemented")


def test_add_new_session_token(live_database_client):
    # Create a new session token locally

    # Call the DatabaseClient method add the session token to the database

    # Fetch the new session token from the database to confirm it was added successfully

    pytest.fail("Test not implemented")


def test_get_user_info_by_session_token(live_database_client):
    # Add a new user to the database

    # Add a session token to the database associated with the user

    # Fetch the user info using its session token with the DatabaseClient method

    # Confirm the user is retrieved successfully

    # Attempt to fetch user using non-existant token

    # Assert TokenNotFoundError error is raised

    pytest.fail("Test not implemented")


def test_delete_session_token(live_database_client):
    # Add a new session token to the database

    # Delete the session token with the DatabaseClient method

    # Confirm the session token was deleted by attempting to fetch it

    pytest.fail("Test not implemented")


def test_get_access_token(live_database_client):
    # Add a new access token to the database

    # Fetch the access token using the DatabaseClient method

    # Confirm that the access token is retrieved

    # Attempt to fetch a non-existant access token

    # Assert AccessTokenNotFoundError is raised

    pytest.fail("Test not implemented")


def test_delete_expired_access_tokens(live_database_client):
    # Add new access tokens to the database, at least two expired and one unexpired

    # Delete the expired access tokens using the DatabaseClient method

    # Confirm that only the expired access tokens were deleted and that all expired tokens were deleted

    pytest.fail("Test not implemented")