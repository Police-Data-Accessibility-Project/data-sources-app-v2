from urllib.parse import quote

from tests.fixtures import dev_db_connection, client_with_db, connection_with_test_data
from tests.helper_functions import (
    create_test_user_api,
    create_api_key,
)


def test_quick_search_get(client_with_db, connection_with_test_data):
    user_info = create_test_user_api(client_with_db)
    api_key = create_api_key(client_with_db, user_info)

    search_term = "Source 1"
    location = "City A"

    # URL encode the search term and location
    encoded_search_term = quote(search_term)
    encoded_location = quote(location)

    response = client_with_db.get(
        f"/quick-search/{encoded_search_term}/{encoded_location}",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    assert response.status_code == 200, "Quick Search endpoint call was not successful"
    data = response.json.get("data")
    assert data["count"] == 1, "Quick Search endpoint response should return only one entry"
    entry = data["data"][0]
    assert entry["agency_name"] == "Agency A"
    assert entry["airtable_uid"] == "SOURCE_UID_1"

