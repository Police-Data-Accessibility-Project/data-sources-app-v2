from http import HTTPStatus
from unittest.mock import MagicMock

import pytest

from tests.helper_scripts.DynamicMagicMock import DynamicMagicMock


class DataSourceByIDWrapperMocks(DynamicMagicMock):
    data_source_by_id_query: MagicMock
    make_response: MagicMock


@pytest.fixture
def data_source_by_id_wrapper_mocks(monkeypatch):
    mock = DataSourceByIDWrapperMocks(
        patch_root="middleware.data_source_queries",
    )
    return mock


def assert_data_source_by_id_wrapper_calls(mock, expected_json: dict):
    mock.data_source_by_id_query.assert_called_with(
        data_source_id="SOURCE_UID_1", db_client=mock.db_client
    )
    mock.make_response.assert_called_with(expected_json, HTTPStatus.OK.value)
