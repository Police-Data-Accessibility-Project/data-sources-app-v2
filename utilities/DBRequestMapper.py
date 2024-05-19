from dataclasses import dataclass, fields
from enum import Enum
from typing import Any, Dict, Type, TypeVar
from collections import namedtuple

DBRequestType = TypeVar("DBRequestType", bound="DBRequestMapper")

# Define named tuples for the subquery results
UpdateQuery = namedtuple("UpdateQuery", ["query", "values"])
InsertQuery = namedtuple("InsertQuery", ["query", "values"])

@dataclass
class DBRequestMapper:
    """
    DBRequestMapper

    This class represents the base form of a dataclass
    used for converting from the JSON request data of an HTTP request to entries in a PostgreSQL database.
    It provides methods for converting the data to and from a dictionary.
    As well as methods for generating insert and update queries.
    """

    @classmethod
    def from_dict(cls: Type[DBRequestType], data: Dict[str, Any]) -> DBRequestType:
        """
        This class method provides a convenient way to create an instance of type DBRequestType
        using the data provided in the input dictionary.
        It filters out any fields that are not present in the class annotations
        and handles special cases for Enum fields.

        :param data: A dictionary containing the data required to instantiate an object
                     of type DBRequestType. The keys of the dictionary represent the field names,
                     and the values represent the corresponding field values.
        :return: An instance of type DBRequestType, populated with the data from the input dictionary.
        """
        filtered_data = {}
        for key, value in data.items():
            if key in cls.__annotations__:
                field_type = cls.__annotations__[key]
                if isinstance(field_type, type) and issubclass(field_type, Enum):
                    try:
                        filtered_data[key] = field_type(value)
                    except ValueError:
                        raise ValueError(f"Invalid value for {key}: {value}")
                else:
                    filtered_data[key] = value

        return cls(**filtered_data)

    def to_dict(self) -> Dict[str, Any]:
        """
        Return a dictionary representation of the object.

        :return: A dictionary representation of the object.
        """
        result = {}
        for field in fields(self):
            value = getattr(self, field.name)
            if value is not None:
                if isinstance(value, Enum):
                    result[field.name] = value.value
                else:
                    result[field.name] = value
        return result

    def create_update_query(
        self, table_name: str, where_column: str, id_value: Any
    ) -> UpdateQuery:
        """
        Create a complete SQL UPDATE query for the instance data.

        :param table_name: The name of the table to update.
        :param where_column: The column to use in the WHERE clause for the id.
        :param id_value: The value of the id to use in the WHERE clause.
        :return: An UpdateQuery named tuple containing the complete query and the values to update.

        Example usage:
            obj = MyDataClass(field1='value1', field2='value2')
            update_query = obj.create_update_query('my_table', 'id', some_id)

            # Use the result in an SQL UPDATE statement
            sql = update_query.query
            values = update_query.values

            # Execute the query
            cursor.execute(sql, values)
        """
        update_data = self.to_dict()
        set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {where_column} = %s"
        values = list(update_data.values()) + [id_value]
        return UpdateQuery(query, values)

    def create_insert_query(self, table_name: str, return_column: str = "id") -> InsertQuery:
        """
        Create a complete SQL INSERT query for the instance data.

        :param return_column: The column name to return upon insertion
        :param table_name: The name of the table to insert into.
        :return: An InsertQuery named tuple containing the complete query and the values to insert.

        Example usage:
            obj = MyDataClass(field1='value1', field2='value2')
            insert_query = obj.create_insert_query('my_table')

            # Use the result in an SQL INSERT statement
            sql = insert_query.query
            values = insert_query.values

            # Execute the query
            cursor.execute(sql, values)
            result_id = cursor.fetchone()[0]
        """
        insert_data = self.to_dict()
        columns = ", ".join(insert_data.keys())
        placeholders = ", ".join(["%s"] * len(insert_data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) RETURNING {return_column}"
        return InsertQuery(query, list(insert_data.values()))
