"""
This module tests that enums representing database objects are
synchronized with the enums within the database.
"""

from enum import Enum
from typing import Type

import psycopg2.extensions

from middleware.database_enums import RequestStatus, RecordType
from tests.middleware.fixtures import db_cursor, dev_db_connection


def get_postgresql_enum_values(cur: psycopg2.extensions.cursor, enum_type: str) -> list:
    """
    Retrieves enum values from database and returns them as a list
    :param cur:
    :param enum_type: The name of the enum type to be retrieved
    :return:
    """
    cur.execute(f"SELECT unnest(enum_range(NULL::{enum_type}))")
    return [row[0] for row in cur.fetchall()]


def get_python_enum_values(enum_class: Type[Enum]) -> list:
    """
    Retrieve enum values from database and return them as a list
    :param enum_class: the enum class to retrieve the enum values from
    :return:
    """
    return [e.value for e in enum_class]


def test_request_status_enum_sync(db_cursor: psycopg2.extensions.cursor):
    """
    RequestStatus enum should be synchronized between Python and Database
    """
    db_enum_values = get_postgresql_enum_values(db_cursor, "request_status")
    python_enum_values = get_python_enum_values(RequestStatus)

    assert set(db_enum_values) == set(
        python_enum_values
    ), f"Mismatch between DB and Python enums: {db_enum_values} != {python_enum_values}"


def test_record_type_enum_sync(db_cursor: psycopg2.extensions.cursor):
    """
    RecordType enum should be synchronized between Python and Database
    """
    db_enum_values = get_postgresql_enum_values(db_cursor, "record_type")
    python_enum_values = get_python_enum_values(RecordType)

    assert set(db_enum_values) == set(
        python_enum_values
    ), f"Mismatch between DB and Python enums: {db_enum_values} != {python_enum_values}"
