from http import HTTPStatus
from typing import Any

from flask import make_response, Response

from database_client.database_client import DatabaseClient
from database_client.result_formatter import ResultFormatter
from middleware.util import format_list_response


class DataSourceNotFoundError(Exception):
    pass


def get_approved_data_sources_wrapper(db_client: DatabaseClient) -> Response:
    raw_results = db_client.get_approved_data_sources()
    zipped_results = ResultFormatter.convert_data_source_matches(raw_results)
    return make_response(
        format_list_response(zipped_results),
        HTTPStatus.OK.value,
    )


def data_source_by_id_wrapper(arg, db_client: DatabaseClient) -> Response:
    try:
        data_source_details = data_source_by_id_query(
            data_source_id=arg, db_client=db_client
        )
        return make_response(data_source_details, HTTPStatus.OK.value)
    except DataSourceNotFoundError:
        return make_response({"message": "Data source not found."}, HTTPStatus.OK.value)


def get_data_sources_for_map_wrapper(db_client: DatabaseClient) -> Response:
    raw_results = db_client.get_data_sources_for_map()
    zipped_results = ResultFormatter.convert_data_source_matches(raw_results)
    return make_response(
        format_list_response(zipped_results),
        HTTPStatus.OK.value,
    )


def update_data_source_wrapper(
    db_client: DatabaseClient, data: dict, data_source_id: str
) -> Response:
    db_client.update_data_source(data, data_source_id)
    return make_response(
        {"message": "Data source updated successfully."}, HTTPStatus.OK
    )


def add_new_data_source_wrapper(db_client: DatabaseClient, data: dict) -> Response:
    db_client.add_new_data_source(data)
    return make_response({"message": "Data source added successfully."}, HTTPStatus.OK)


def data_source_by_id_query(
    data_source_id: str,
    db_client: DatabaseClient,
) -> dict[str, Any]:
    """
    Processes a request to fetch data source details by ID from the database

    :param data_source_id: The unique identifier for the data source.
    :param db_client: A database client object.
    :return: A dictionary with the data source details after processing.
    """
    raw_results = db_client.get_data_source_by_id(data_source_id)
    if not raw_results:
        raise DataSourceNotFoundError("The specified data source was not found.")

    return ResultFormatter.zip_get_data_source_by_id_results(raw_results)


def needs_identification_data_sources_wrapper(db_client: DatabaseClient) -> Response:
    raw_results = db_client.get_needs_identification_data_sources()
    zipped_results = ResultFormatter.convert_data_source_matches(
        raw_results
    )
    return make_response(
        format_list_response(zipped_results),
        HTTPStatus.OK.value,
    )

