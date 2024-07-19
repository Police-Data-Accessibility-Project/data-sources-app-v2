"""
Helper scripts for the Resource classes
"""

from flask_restx import Namespace, Model, fields
from flask_restx.reqparse import RequestParser


def add_api_key_header_arg(parser: RequestParser):
    parser.add_argument(
        "Authorization",
        type=str,
        required=True,
        location="headers",
        help="API key required to access this endpoint",
        default="Bearer YOUR_API_KEY",
    )


def create_user_model(namespace: Namespace) -> Model:
    return namespace.model(
        "User",
        {
            "email": fields.String(required=True, description="The email of the user"),
            "password": fields.String(
                required=True, description="The password of the user"
            ),
        },
    )


def create_search_model(namespace: Namespace) -> Model:
    search_result_inner_model = namespace.model(
        "SearchResultInner",
        {
            "airtable_uid": fields.String(
                required=True, description="Airtable UID of the record"
            ),
            "agency_name": fields.String(description="Name of the agency"),
            "municipality": fields.String(description="Name of the municipality"),
            "state_iso": fields.String(description="ISO code of the state"),
            "data_source_name": fields.String(description="Name of the data source"),
            "description": fields.String(description="Description of the record"),
            "record_type": fields.String(description="Type of the record"),
            "source_url": fields.String(description="URL of the data source"),
            "record_format": fields.String(description="Format of the record"),
            "coverage_start": fields.String(description="Coverage start date"),
            "coverage_end": fields.String(description="Coverage end date"),
            "agency_supplied": fields.String(
                description="If the record is supplied by the agency"
            ),
        },
    )

    search_result_outer_model = namespace.model(
        "SearchResultOuter",
        {
            "count": fields.Integer(
                required=True, description="Count of data items", attribute="count"
            ),
            "data": fields.List(
                fields.Nested(
                    search_result_inner_model,
                    required=True,
                    description="List of data items",
                ),
                attribute="data",
            ),
        },
    )
    return search_result_outer_model