from dataclasses import dataclass
from typing import Type, Optional, Callable

from flask_restx import Model
from flask_restx.reqparse import RequestParser
from marshmallow import Schema

from middleware.schema_and_dto_logic.custom_types import SchemaTypes, DTOTypes
from utilities.enums import SourceMappingEnum


@dataclass
class FlaskRestxDocInfo:
    parser: RequestParser
    model: Optional[Model] = None


@dataclass
class SchemaPopulateParameters:
    schema: SchemaTypes
    dto_class: Type[DTOTypes]


@dataclass
class DTOPopulateParameters:
    """
    Parameters for the dynamic DTO population function
    """

    dto_class: Type[DTOTypes]
    source: Optional[SourceMappingEnum] = None
    transformation_functions: Optional[dict[str, Callable]] = None
    attribute_source_mapping: Optional[dict[str, SourceMappingEnum]] = None
    # A schema to be used for validating the input of the class.
    validation_schema: Optional[Type[Schema]] = None
