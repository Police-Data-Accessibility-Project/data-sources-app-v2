import psycopg2

from middleware.quick_search_query import (
    unaltered_search_query,
    quick_search_query,
    QUICK_SEARCH_COLUMNS,
)
from tests.middleware.helper_functions import (
    has_expected_keys,
    get_most_recent_quick_search_query_log,
)
from tests.fixtures import (
    connection_with_test_data, cursor_with_test_data, dev_db_connection
)


def test_unaltered_search_query(
    cursor_with_test_data: psycopg2.extensions.cursor,
) -> None:
    """
    :param cursor_with_test_data:
    :return: None
    Test the unaltered_search_query method properly returns only one result
    """
    response = unaltered_search_query(
        cursor_with_test_data, search="Source 1", location="City A"
    )

    assert len(response) == 1
    assert response[0][3] == "Type A"  # Record Type


def test_quick_search_query_logging(
    cursor_with_test_data: psycopg2.extensions.cursor,
) -> None:
    """
    Tests that quick_search_query properly creates a log of the query

    :param connection_with_test_data:
    :return: None
    """
    # Get datetime of test

    cursor_with_test_data.execute("SELECT NOW()")
    result = cursor_with_test_data.fetchone()
    test_datetime = result[0]

    quick_search_query(
        search="Source 1", location="City A", cursor=cursor_with_test_data
    )

    # Test that query inserted into log
    result = get_most_recent_quick_search_query_log(cursor_with_test_data, "Source 1", "City A")
    assert result.result_count == 1
    assert result.updated_at >= test_datetime


def test_quick_search_query_results(
    cursor_with_test_data: psycopg2.extensions.cursor,
) -> None:
    """
    Test the `quick_search_query` method returns expected test data

    :param cursor_with_test_data:
    :return: None
    """
    # TODO: Something about the quick_search_query might be mucking up the savepoints. Address once you fix quick_search's logic issues
    results = quick_search_query(
        search="Source 1", location="City A", cursor=cursor_with_test_data
    )
    # Test that results include expected keys
    assert has_expected_keys(results["data"][0].keys(), QUICK_SEARCH_COLUMNS)
    assert len(results["data"]) == 1
    assert results["data"][0]["record_type"] == "Type A"
    # "Source 3" was listed as pending and shouldn't show up
    results = quick_search_query(
        search="Source 3", location="City C", cursor=cursor_with_test_data
    )
    assert len(results["data"]) == 0
