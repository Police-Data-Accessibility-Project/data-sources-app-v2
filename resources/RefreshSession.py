from http import HTTPStatus

from flask import Response
from flask_jwt_extended import jwt_required
from flask_restx import fields

from middleware.access_logic import (
    WRITE_ONLY_AUTH_INFO,
    STANDARD_JWT_AUTH_INFO,
    AccessInfoPrimary,
)
from middleware.decorators import endpoint_info
from middleware.primary_resource_logic.login_queries import (
    refresh_session,
)
from resources.endpoint_schema_config import SchemaConfigs
from resources.resource_helpers import ResponseInfo

from utilities.namespace import create_namespace, AppNamespaces
from resources.PsycopgResource import PsycopgResource, handle_exceptions

namespace_refresh_session = create_namespace(AppNamespaces.AUTH)


@namespace_refresh_session.route("/refresh-session")
class RefreshSession(PsycopgResource):
    """
    Provides a resource for refreshing a user's session token.
    If the provided session token is valid and not expired, it is replaced with a new one.
    """

    @endpoint_info(
        namespace=namespace_refresh_session,
        auth_info=STANDARD_JWT_AUTH_INFO,
        description="Allows a user to refresh their session token.",
        response_info=ResponseInfo(success_message="Session token refreshed."),
        schema_config=SchemaConfigs.REFRESH_SESSION,
    )
    def post(self, access_info: AccessInfoPrimary) -> Response:
        """
        Processes the session token refresh request. If the provided session token is valid,
        it generates a new session token, invalidates the old one, and returns the new token.

        Returns:
        - A dictionary containing a message of success or failure, and the new session token if successful.
        """

        return self.run_endpoint(
            wrapper_function=refresh_session,
            schema_populate_parameters=SchemaConfigs.REFRESH_SESSION.value.get_schema_populate_parameters(),
            access_info=access_info,
        )
