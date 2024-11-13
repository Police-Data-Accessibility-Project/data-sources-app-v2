"""
Class based means to run and validate requests
"""
from http import HTTPStatus
from typing import Optional, Type, Union

from flask.testing import FlaskClient
from marshmallow import Schema

from tests.helper_scripts.helper_functions import get_authorization_header
from tests.helper_scripts.run_and_validate_request import http_methods, run_and_validate_request


class RequestValidator:

    def __init__(self, flask_client: FlaskClient):
        self.flask_client = flask_client

    def post(
        self,
        endpoint: str,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_json_content: Optional[dict] = None,
        expected_schema: Optional[Union[Type[Schema], Schema]] = None,
        query_parameters: Optional[dict] = None,
        **request_kwargs,
    ):
        return run_and_validate_request(
            flask_client=self.flask_client,
            http_method="post",
            endpoint=endpoint,
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
            expected_schema=expected_schema,
            query_parameters=query_parameters,
            **request_kwargs,
        )

    def get(
        self,
        endpoint: str,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_json_content: Optional[dict] = None,
        expected_schema: Optional[Union[Type[Schema], Schema]] = None,
        query_parameters: Optional[dict] = None,
        **request_kwargs,
    ):
        return run_and_validate_request(
            flask_client=self.flask_client,
            http_method="get",
            endpoint=endpoint,
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
            expected_schema=expected_schema,
            query_parameters=query_parameters,
            **request_kwargs,
        )

    def put(
        self,
        endpoint: str,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_json_content: Optional[dict] = None,
        expected_schema: Optional[Union[Type[Schema], Schema]] = None,
        query_parameters: Optional[dict] = None,
        **request_kwargs,
    ):
        return run_and_validate_request(
            flask_client=self.flask_client,
            http_method="put",
            endpoint=endpoint,
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
            expected_schema=expected_schema,
            query_parameters=query_parameters,
            **request_kwargs,
        )

    def delete(
        self,
        endpoint: str,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_json_content: Optional[dict] = None,
        expected_schema: Optional[Union[Type[Schema], Schema]] = None,
        query_parameters: Optional[dict] = None,
        **request_kwargs,
    ):
        return run_and_validate_request(
            flask_client=self.flask_client,
            http_method="delete",
            endpoint=endpoint,
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content,
            expected_schema=expected_schema,
            query_parameters=query_parameters,
            **request_kwargs,
        )

    # Below are shorthands for common requests

    def login(self, email: str, password: str, expected_response_status: HTTPStatus = HTTPStatus.OK):
        return self.post(
            endpoint="/api/login",
            json={"email": email, "password": password},
            expected_response_status=expected_response_status
        )

    def reset_password(
            self,
            token: str,
            password: str,
            expected_response_status: HTTPStatus = HTTPStatus.OK
    ):
        return self.post(
            endpoint="/api/reset-password",
            headers=get_authorization_header(scheme="Bearer", token=token),
            json={"password": password},
            expected_response_status=expected_response_status
        )

    def request_reset_password(
            self,
            email: str,
            mocker,
            expected_response_status: HTTPStatus = HTTPStatus.OK):
        mock = mocker.patch(
            "middleware.primary_resource_logic.reset_token_queries.send_password_reset_link"
        )
        response = self.post(
            endpoint="/api/request-reset-password",
            json={"email": email},
            expected_response_status=expected_response_status
        )
        return mock.call_args[1]["token"]

    def reset_token_validation(
        self,
        token: str,
        expected_response_status: HTTPStatus = HTTPStatus.OK,
        expected_json_content: Optional[dict] = None
    ):
        return self.post(
            endpoint="/api/reset-token-validation",
            headers=get_authorization_header(scheme="Bearer", token=token),
            expected_response_status=expected_response_status,
            expected_json_content=expected_json_content
        )