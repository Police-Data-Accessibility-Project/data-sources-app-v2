import psycopg2
import pytest
from tests.fixtures import connection_with_test_data, dev_db_connection, client_with_db
from tests.helper_functions import create_test_user_api, create_api_key


def test_data_sources_map_get(
    client_with_db, connection_with_test_data: psycopg2.extensions.connection
):
    user_info = create_test_user_api(client_with_db)
    api_key = create_api_key(client_with_db, user_info)
    response = client_with_db.get(
        "/data-sources-map",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert response.status_code == 200
    data = response.json["data"]
    found_source = False
    for result in data:
        name = result["name"]
        if name != "Source 1":
            continue
        found_source = True
        assert result["lat"] == 30
        assert result["lng"] == 20
    assert found_source