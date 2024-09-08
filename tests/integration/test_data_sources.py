"""Integration tests for /data-sources endpoint"""
import urllib.parse
import uuid

import psycopg

from database_client.database_client import DatabaseClient
from middleware.models import DataSource
from tests.fixtures import (
    connection_with_test_data,
    flask_client_with_db,
    db_client_with_test_data,
    test_user_admin,
    dev_db_connection
)
from tests.helper_scripts.helper_functions import (
    get_boolean_dictionary,
    create_test_user_setup,
    search_with_boolean_dictionary,
)
from tests.helper_scripts.common_test_functions import run_and_validate_request

ENDPOINT = "/api/data-sources/"


def test_data_sources_get(
    flask_client_with_db, connection_with_test_data: psycopg.Connection
):
    """
    Test that GET call to /data-sources endpoint retrieves data sources and correctly identifies specific sources by name
    """
    inserted_data_sources_found = get_boolean_dictionary(
        ("Source 1", "Source 2", "Source 3")
    )
    tus = create_test_user_setup(flask_client_with_db)
    response_json = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint=f"{ENDPOINT}page/1",  # ENDPOINT,
        headers=tus.api_authorization_header,
    )
    data = response_json["data"]
    search_with_boolean_dictionary(
        data=data,
        boolean_dictionary=inserted_data_sources_found,
        key_to_search_on="name",
    )
    assert inserted_data_sources_found["Source 1"]
    # The below are not approved, and so should not be found
    assert not inserted_data_sources_found["Source 2"]
    assert not inserted_data_sources_found["Source 3"]

    # Test sort functionality
    response_json = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint=f"{ENDPOINT}page/1?sort_by=name&sort_order=ASC",
        headers=tus.api_authorization_header,
    )
    data_asc = response_json["data"]

    response_json = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint=f"{ENDPOINT}page/1?sort_by=name&sort_order=DESC",
        headers=tus.api_authorization_header,
    )
    data_desc = response_json["data"]

    assert data_asc[0]["name"] < data_desc[0]["name"]

def test_data_sources_get_many_limit_columns(
    flask_client_with_db, connection_with_test_data: psycopg.Connection
):
    """
    Test that GET call to /data-sources endpoint properly limits by columns
     when passed the `requested_columns` query parameter
    """

    tus = create_test_user_setup(flask_client_with_db)
    allowed_columns = ["name", "submitted_name", "airtable_uid"]
    url_encoded_column_string = urllib.parse.quote_plus(str(allowed_columns))
    response_json = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint=f"{ENDPOINT}page/1?requested_columns={url_encoded_column_string}",
        headers=tus.api_authorization_header,
    )
    data = response_json["data"]

    entry = data[0]
    for column in allowed_columns:
        assert column in entry



def test_data_sources_post(
    flask_client_with_db,
    db_client_with_test_data: DatabaseClient,
    test_user_admin,
):
    """
    Test that POST call to /data-sources endpoint successfully creates a new data source with a unique name and verifies its existence in the database
    """

    name = str(uuid.uuid4())
    airtable_uid = str(uuid.uuid4())
    json = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="post",
        endpoint=ENDPOINT,
        headers=test_user_admin.jwt_authorization_header,
        json={
            "entry_data": {
                "name": name,
                "airtable_uid": airtable_uid,
            }
        },
    )
    assert json is not None
    rows = db_client_with_test_data.execute_raw_sql(
        query="""
        SELECT * from data_sources WHERE name=%s
        """,
        vars=(name,),
    )
    len(rows) == 1



def test_data_sources_by_id_get(
    flask_client_with_db, connection_with_test_data: psycopg.Connection
):
    """
    Test that GET call to /data-sources-by-id/<data_source_id> endpoint retrieves the data source with the correct homepage URL
    """

    tus = create_test_user_setup(flask_client_with_db)
    response_json = run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="get",
        endpoint=f"{ENDPOINT}id/SOURCE_UID_1",
        headers=tus.api_authorization_header,
    )
    assert response_json["data"]["source_url"] == "http://src1.com"


def test_data_sources_by_id_put(
    flask_client_with_db, db_client_with_test_data: DatabaseClient, test_user_admin
):
    """
    Test that PUT call to /data-sources-by-id/<data_source_id> endpoint successfully updates the description of the data source and verifies the change in the database
    """

    desc = str(uuid.uuid4())
    run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="put",
        endpoint=f"/api/data-sources/id/SOURCE_UID_1",
        headers=test_user_admin.jwt_authorization_header,
        json={
            "entry_data": {"description": desc},
        },
    )

    result = db_client_with_test_data.get_data_sources(
        columns=[DataSource.description],
        where_mappings=[
            DataSource.airtable_uid == "SOURCE_UID_1"
        ]
    )
    assert result[0]["description"] == desc

def test_data_sources_by_id_delete(
    flask_client_with_db, db_client_with_test_data: DatabaseClient, test_user_admin
):
    """
    Test that DELETE call to /data-sources-by-id/<data_source_id> endpoint successfully deletes the data source and verifies the change in the database
    """
    # Insert new entry

    airtable_uid = db_client_with_test_data._create_entry_in_table(
        "data_sources",
        column_value_mappings={
            "airtable_uid": uuid.uuid4().hex,
            "name": "Test",
            "description": "Test",
            "source_url": "http://src1.com",
            "approval_status": "approved",
            "url_status": "available",
            "record_type": "Type A",
        },
        column_to_return="airtable_uid",
    )


    result = db_client_with_test_data.get_data_sources(
        columns=[DataSource.description],
        where_mappings=[
            DataSource.airtable_uid == airtable_uid
        ]
    )
    assert len(result) == 1

    run_and_validate_request(
        flask_client=flask_client_with_db,
        http_method="delete",
        endpoint=f"{ENDPOINT}id/{airtable_uid}",
        headers=test_user_admin.jwt_authorization_header,
    )

    result = db_client_with_test_data.get_data_sources(
        columns=[DataSource.description],
        where_mappings=[
            DataSource.airtable_uid == airtable_uid
        ]
    )

    assert len(result) == 0