import psycopg2
import pytest
from tests.fixtures import connection_with_test_data, dev_db_connection, client_with_db
from tests.helper_functions import (
    get_boolean_dictionary,
    create_test_user_api,
    create_api_key,
)


def test_data_sources_needs_identification(
    client_with_db, connection_with_test_data: psycopg2.extensions.connection
):
    inserted_data_sources_found = get_boolean_dictionary(
        ("Source 1", "Source 2", "Source 3")
    )
    user_info = create_test_user_api(client_with_db)
    api_key = create_api_key(client_with_db, user_info)
    response = client_with_db.get(
        "/data-sources-needs-identification",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert response.status_code == 200

    for result in response.json["data"]:
        name = result["name"]
        if name in inserted_data_sources_found:
            inserted_data_sources_found[name] = True

    assert not inserted_data_sources_found["Source 1"]
    assert inserted_data_sources_found["Source 2"]
    assert not inserted_data_sources_found["Source 3"]
