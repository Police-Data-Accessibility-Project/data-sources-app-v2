"""This module contains helper functions used by middleware pytests."""

import uuid
from collections import namedtuple
from typing import Optional
from http import HTTPStatus
from unittest.mock import MagicMock

import psycopg2.extensions
from flask.testing import FlaskClient

from middleware.dataclasses import (
    GithubUserInfo,
    OAuthCallbackInfo,
    FlaskSessionCallbackInfo,
)
from middleware.enums import CallbackFunctionsEnum
from tests.helper_scripts.common_test_data import TEST_RESPONSE

TestTokenInsert = namedtuple("TestTokenInsert", ["id", "email", "token"])
TestUser = namedtuple("TestUser", ["id", "email", "password_hash"])


def insert_test_agencies_and_sources(cursor: psycopg2.extensions.cursor) -> None:
    """
    Insert test agencies and sources into database.

    :param cursor:
    :return:
    """
    cursor.execute(
        """
        INSERT INTO
        PUBLIC.DATA_SOURCES (
            airtable_uid,
            NAME,
            DESCRIPTION,
            RECORD_TYPE,
            SOURCE_URL,
            APPROVAL_STATUS,
            URL_STATUS
        )
        VALUES
        ('SOURCE_UID_1','Source 1','Description of src1',
            'Type A','http://src1.com','approved','available'),
        ('SOURCE_UID_2','Source 2','Description of src2',
            'Type B','http://src2.com','needs identification','available'),
        ('SOURCE_UID_3','Source 3', 'Description of src3',
            'Type C', 'http://src3.com', 'pending', 'available');

        INSERT INTO public.agencies
        (airtable_uid, name, municipality, state_iso,
            county_name, count_data_sources, lat, lng)
        VALUES 
            ('Agency_UID_1', 'Agency A', 'City A',
                'CA', 'County X', 3, 30, 20),
            ('Agency_UID_2', 'Agency B', 'City B',
                'NY', 'County Y', 2, 40, 50),
            ('Agency_UID_3', 'Agency C', 'City C',
                'TX', 'County Z', 1, 90, 60);

        INSERT INTO public.agency_source_link
        (airtable_uid, agency_described_linked_uid)
        VALUES
            ('SOURCE_UID_1', 'Agency_UID_1'),
            ('SOURCE_UID_2', 'Agency_UID_2'),
            ('SOURCE_UID_3', 'Agency_UID_3');
        """
    )


def insert_test_agencies_and_sources_if_not_exist(cursor: psycopg2.extensions.cursor):
    try:
        cursor.execute("SAVEPOINT my_savepoint")
        insert_test_agencies_and_sources(cursor)
    except psycopg2.errors.UniqueViolation:  # Data already inserted
        cursor.execute("ROLLBACK TO SAVEPOINT my_savepoint")


def get_reset_tokens_for_email(
    db_cursor: psycopg2.extensions.cursor, reset_token_insert: TestTokenInsert
) -> tuple:
    """
    Get all reset tokens associated with an email.

    :param db_cursor:
    :param reset_token_insert:
    :return:
    """
    db_cursor.execute(
        """
        SELECT email from RESET_TOKENS where email = %s
        """,
        (reset_token_insert.email,),
    )
    results = db_cursor.fetchall()
    return results


def create_reset_token(cursor: psycopg2.extensions.cursor) -> TestTokenInsert:
    """
    Create a test user and associated reset token.

    :param cursor:
    :return:
    """
    user = create_test_user(cursor)
    token = uuid.uuid4().hex
    cursor.execute(
        """
        INSERT INTO reset_tokens(email, token)
        VALUES (%s, %s)
        RETURNING id
        """,
        (user.email, token),
    )
    id = cursor.fetchone()[0]
    return TestTokenInsert(id=id, email=user.email, token=token)


def check_is_test_response(response):
    check_response_status(response, TEST_RESPONSE.status_code)
    assert response.json == TEST_RESPONSE.response


def create_test_user(
    cursor,
    email="",
    password_hash="hashed_password_here",
    api_key="api_key_here",
    role=None,
) -> TestUser:
    """
    Create test user and return the id of the test user.

    :param cursor:
    :return: user id
    """
    if email == "":
        email = uuid.uuid4().hex + "@test.com"
    cursor.execute(
        """
        INSERT INTO users (email, password_digest, api_key, role)
        VALUES
        (%s, %s, %s, %s)
        RETURNING id;
        """,
        (email, password_hash, api_key, role),
    )
    return TestUser(
        id=cursor.fetchone()[0],
        email=email,
        password_hash=password_hash,
    )


QuickSearchQueryLogResult = namedtuple(
    "QuickSearchQueryLogResult", ["result_count", "updated_at", "results"]
)


def get_most_recent_quick_search_query_log(
    cursor: psycopg2.extensions.cursor, search: str, location: str
) -> Optional[QuickSearchQueryLogResult]:
    """
    Retrieve most recent quick search query log for a search and location.

    :param cursor: The Cursor object of the database connection.
    :param search: The search query string.
    :param location: The location string.
    :return: A QuickSearchQueryLogResult object
        containing the result count and updated timestamp.
    """
    cursor.execute(
        """
        SELECT RESULT_COUNT, CREATED_AT, RESULTS FROM QUICK_SEARCH_QUERY_LOGS WHERE
        search = %s AND location = %s ORDER BY CREATED_AT DESC LIMIT 1
        """,
        (search, location),
    )
    result = cursor.fetchone()
    if result is None:
        return result
    return QuickSearchQueryLogResult(
        result_count=result[0], updated_at=result[1], results=result[2]
    )


def has_expected_keys(result_keys: list, expected_keys: list) -> bool:
    """
    Check that given result includes expected keys.

    :param result:
    :param expected_keys:
    :return: True if has expected keys, false otherwise
    """
    return not set(expected_keys).difference(result_keys)


def get_boolean_dictionary(keys: tuple) -> dict:
    """
    Creates dictionary of booleans, all set to false.

    :param keys:
    :return: dictionary of booleans
    """
    d = {}
    for key in keys:
        d[key] = False
    return d


UserInfo = namedtuple("UserInfo", ["email", "password"])


def create_test_user_api(client: FlaskClient) -> UserInfo:
    """
    Create a test user through calling the /user endpoint via the Flask API
    :param client:
    :return:
    """
    email = str(uuid.uuid4())
    password = str(uuid.uuid4())
    response = client.post(
        "user",
        json={"email": email, "password": password},
    )
    check_response_status(response, HTTPStatus.OK.value)
    return UserInfo(email=email, password=password)


def login_and_return_session_token(
    client_with_db: FlaskClient, user_info: UserInfo
) -> str:
    """
    Login as a given user and return the associated session token,
    using the /login endpoint of the Flask API
    :param client_with_db:
    :param user_info:
    :return:
    """
    response = client_with_db.post(
        "/api/login",
        json={"email": user_info.email, "password": user_info.password},
    )
    assert response.status_code == HTTPStatus.OK.value, "User login unsuccessful"
    session_token = response.json.get("data")
    return session_token


def get_user_password_digest(cursor: psycopg2.extensions.cursor, user_info):
    """
    Get the associated password digest of a user (given their email) from the database
    :param cursor:
    :param user_info:
    :return:
    """
    cursor.execute(
        """
        SELECT password_digest from users where email = %s
    """,
        (user_info.email,),
    )
    return cursor.fetchone()[0]


def request_reset_password_api(client_with_db, mocker, user_info):
    """
    Send a request to reset password via a Flask call to the /request-reset-password endpoint
    and return the reset token
    :param client_with_db:
    :param mocker:
    :param user_info:
    :return:
    """
    mocker.patch("middleware.reset_token_queries.send_password_reset_link")
    response = client_with_db.post(
        "/api/request-reset-password", json={"email": user_info.email}
    )
    token = response.json.get("token")
    return token


def create_api_key(client_with_db, user_info) -> str:
    """
    Obtain an api key for the given user, via a Flask call to the /api-key endpoint
    :param client_with_db:
    :param user_info:
    :return: api_key
    """
    response = client_with_db.get(
        "/api/api_key", json={"email": user_info.email, "password": user_info.password}
    )
    assert (
        response.status_code == HTTPStatus.OK.value
    ), "API key creation not successful"
    api_key = response.json.get("api_key")
    return api_key


def create_api_key_db(cursor, user_id: str):
    api_key = uuid.uuid4().hex
    cursor.execute("UPDATE users SET api_key = %s WHERE id = %s", (api_key, user_id))
    return api_key


def insert_test_data_source(cursor: psycopg2.extensions.cursor) -> str:
    """
    Insert test data source and return id
    :param cursor:
    :return: randomly generated uuid
    """
    test_uid = str(uuid.uuid4())
    cursor.execute(
        """
        INSERT INTO
        PUBLIC.DATA_SOURCES (
            airtable_uid,
            NAME,
            DESCRIPTION,
            RECORD_TYPE,
            SOURCE_URL,
            APPROVAL_STATUS,
            URL_STATUS
        )
        VALUES
        (%s,'Example Data Source', 'Example Description',
            'Type A','http://src1.com','approved','available')
        """,
        (test_uid,),
    )
    return test_uid


def give_user_admin_role(
    connection: psycopg2.extensions.connection, user_info: UserInfo
):
    """
    Give the given user an admin role.
    :param connection:
    :param user_info:
    :return:
    """
    cursor = connection.cursor()

    cursor.execute(
        """
    UPDATE users
    SET role = 'admin'
    WHERE email = %s
    """,
        (user_info.email,),
    )


def check_response_status(response, status_code):
    assert (
        response.status_code == status_code
    ), f"Expected status code {status_code}, got {response.status_code}: {response.text}"


def setup_get_typeahead_suggestion_test_data(cursor: psycopg2.extensions.cursor):
    try:
        cursor.execute("SAVEPOINT typeahead_suggestion_test_savepoint")

        # State (via state_names table)
        cursor.execute(
            "insert into state_names (state_iso, state_name) values ('XY', 'Xylonsylvania')"
        )
        # County (via counties table)
        cursor.execute(
            "insert into counties(fips, name, state_iso) values ('12345', 'Arxylodon', 'XY')"
        )

        # Locality (via agencies table)
        cursor.execute(
            """insert into agencies 
            (name, airtable_uid, municipality, state_iso, county_fips, county_name) 
            values 
            ('Xylodammerung Police Agency', 'XY_SOURCE_UID', 'Xylodammerung', 'XY', '12345', 'Arxylodon')"""
        )

        # Refresh materialized view
        cursor.execute("CALL refresh_typeahead_suggestions();")
    except psycopg2.errors.UniqueViolation:
        cursor.execute("ROLLBACK TO SAVEPOINT typeahead_suggestion_test_savepoint")


def assert_is_oauth_redirect_link(text: str):
    assert "https://github.com/login/oauth/authorize?response_type=code" in text, (
        "Expected OAuth authorize link, got: " + text
    )


def patch_post_callback_functions(
    monkeypatch,
    github_user_info: GithubUserInfo,
    callback_functions_enum: CallbackFunctionsEnum,
    callback_params: dict,
):
    mock_get_oauth_callback_info = MagicMock(
        return_value=OAuthCallbackInfo(github_user_info)
    )
    mock_get_flask_session_callback_info = MagicMock(
        return_value=FlaskSessionCallbackInfo(
            callback_functions_enum=callback_functions_enum,
            callback_params=callback_params,
        )
    )
    monkeypatch.setattr(
        "middleware.callback_primary_logic.get_oauth_callback_info",
        mock_get_oauth_callback_info,
    )
    monkeypatch.setattr(
        "middleware.callback_primary_logic.get_flask_session_callback_info",
        mock_get_flask_session_callback_info,
    )


def patch_setup_callback_session(
    monkeypatch,
    resources_module_name: str,
) -> MagicMock:
    mock_setup_callback_session = MagicMock()
    monkeypatch.setattr(
        f"resources.{resources_module_name}.setup_callback_session",
        mock_setup_callback_session,
    )
    return mock_setup_callback_session


def create_fake_github_user_info(email: Optional[str] = None) -> GithubUserInfo:
    return GithubUserInfo(
        user_id=uuid.uuid4().hex,
        user_email=uuid.uuid4().hex if email is None else email,
    )


def assert_expected_pre_callback_response(response):
    check_response_status(response, HTTPStatus.FOUND)
    response_text = response.text
    assert_is_oauth_redirect_link(response_text)


def assert_session_token_exists_for_email(
    cursor: psycopg2.extensions.cursor, session_token: str, email: str
):
    cursor.execute(
        """
    SELECT email
    FROM session_tokens
    WHERE token = %s
    """,
        (session_token,),
    )
    rows = cursor.fetchall()
    assert len(rows) == 1, "Session token should only exist once in database"

    row = rows[0]
    assert row[0] == email, "Email in session_tokens table does not match user email"

TestUserSetup = namedtuple(
    "TestUserSetup", ["user_info", "api_key", "authorization_header"])

def create_test_user_setup(client: FlaskClient) -> TestUserSetup:
    user_info = create_test_user_api(client)
    api_key = create_api_key(client, user_info)
    authorization_header = {
        "Authorization": f"Bearer {api_key}"
    }
    return TestUserSetup(user_info, api_key, authorization_header)