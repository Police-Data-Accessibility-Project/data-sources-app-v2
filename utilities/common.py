import datetime
import re
import json
from enum import Enum
from typing import TypeVar, Type


def convert_dates_to_strings(data_dict):
    for key, value in data_dict.items():
        if isinstance(value, datetime.date):
            data_dict[key] = value.strftime("%Y-%m-%d")
    return data_dict


def format_arrays(data_dict):
    for key, value in data_dict.items():
        if value is not None and type(value) is str:
            if re.search(r"\"?\[ ?\".*\"\ ?]\"?", value, re.DOTALL):
                data_dict[key] = json.loads(value.strip('"'))
    return data_dict


# Define a generic type variable that is bound to Enum
ENUM_TYPE = TypeVar("ENUM_TYPE", bound=Enum)


def str_to_enum(enum_class: Type[ENUM_TYPE], value: str) -> ENUM_TYPE:
    """Converts a string to an enum value"""
    try:
        return enum_class(value)
    except ValueError:
        raise ValueError(f"'{value}' is not a valid {enum_class.__name__}")
