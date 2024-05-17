import pytest
from dataclasses import dataclass
from enum import Enum

from utilities.DBRequestMapper import DBRequestMapper


class Status(Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'

@dataclass
class TestDBRequestMapper(DBRequestMapper):
    field1: str
    field2: int
    status: Status

def test_from_dict():
    data = {
        'field1': 'test_value',
        'field2': 42,
        'status': 'active'
    }
    obj = TestDBRequestMapper.from_dict(data)
    assert obj.field1 == 'test_value'
    assert obj.field2 == 42
    assert obj.status == Status.ACTIVE

def test_to_dict():
    obj = TestDBRequestMapper(field1='test_value', field2=42, status=Status.ACTIVE)
    data = obj.to_dict()
    expected_data = {
        'field1': 'test_value',
        'field2': 42,
        'status': 'active'
    }
    assert data == expected_data

def test_create_update_query():
    obj = TestDBRequestMapper(field1='test_value', field2=42, status=Status.ACTIVE)
    update_query = obj.create_update_query('my_table', 'id', 1)
    expected_query = "UPDATE my_table SET field1 = %s, field2 = %s, status = %s WHERE id = %s"
    expected_values = ['test_value', 42, 'active', 1]
    assert update_query.query == expected_query
    assert update_query.values == expected_values

def test_create_insert_query():
    obj = TestDBRequestMapper(field1='test_value', field2=42, status=Status.ACTIVE)
    insert_query = obj.create_insert_query('my_table')
    expected_query = "INSERT INTO my_table (field1, field2, status) VALUES (%s, %s, %s) RETURNING id"
    expected_values = ['test_value', 42, 'active']
    assert insert_query.query == expected_query
    assert insert_query.values == expected_values
