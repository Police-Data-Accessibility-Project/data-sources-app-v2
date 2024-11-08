from flask import Response, redirect

from database_client.database_client import DatabaseClient
from database_client.enums import ExternalAccountTypeEnum
from middleware.common_response_formatting import message_response
from middleware.exceptions import UserNotFoundError
from middleware.flask_response_manager import FlaskResponseManager
from middleware.primary_resource_logic.login_queries import (
    unauthorized_response,
    login_response,
)
from middleware.third_party_interaction_logic.callback_flask_sessions_logic import (
    get_callback_params,
    get_callback_function,
)
from middleware.custom_dataclasses import (
    FlaskSessionCallbackInfo,
)
from middleware.third_party_interaction_logic.callback_oauth_logic import (
    get_github_oauth_access_token,
)
from tests.helper_scripts.helper_functions import add_query_params


def get_flask_session_callback_info() -> FlaskSessionCallbackInfo:
    """
    Returns a FlaskSessionCallbackInfo object with the callback function and parameters
    :return:
    """
    return FlaskSessionCallbackInfo(
        callback_functions_enum=get_callback_function(),
        callback_params=get_callback_params(),
    )


def callback_outer_wrapper(db_client: DatabaseClient) -> Response:
    """
    Outer wrapper for the callback function.
    This wrapper interfaces with the functions which interface with the Flask Sessions and OAuth2 logic
    and passes the results into the callback_inner_wrapper
    :param db_client:
    :return:
    """
    gh_access_token = get_github_oauth_access_token()
    flask_session_callback_info = get_flask_session_callback_info()
    redirect_base_url = flask_session_callback_info.callback_params["redirect_url"]
    redirect_url = add_query_params(
        url=redirect_base_url,
        params={"gh_access_token": gh_access_token['access_token']},
    )
    return redirect(
        location=redirect_url
    )




def get_github_user_info(access_token: str) -> GithubUserInfo:
    """
    Gets the user information from the Github API via OAuth2
    :param access_token: The access token from the Github API
    :return: The user information
    """
    return GithubUserInfo(
        user_id=get_github_user_id(access_token),
        user_email=get_github_user_email(access_token),
    )


def user_exists(db_client: DatabaseClient, email: str) -> bool:
    try:
        db_client.get_user_info(email=email)
        return True
    except UserNotFoundError:
        return False


def try_logging_in_with_github_id(
    db_client: DatabaseClient, github_user_info: GithubUserInfo
) -> Response:
    """
    Tries to log in a user.

    :param github_user_info: GithubUserInfo object.
    :param db_client: DatabaseClient object.
    :return: A response object with a message and status code.
    """
    try:
        user_info_gh = db_client.get_user_info_by_external_account_id(
            external_account_id=str(github_user_info.user_id),
            external_account_type=ExternalAccountTypeEnum.GITHUB,
        )
    except UserNotFoundError:
        # Check if user email exists
        if user_exists(db_client=db_client, email=github_user_info.user_email):
            return message_response(
                status_code=HTTPStatus.UNAUTHORIZED,
                message=f"User with email {github_user_info.user_email} already exists exists but is not linked to"
                f" the Github Account with the same email. You must explicitly link their accounts in order to log in via Github.",
            )

        create_user_with_github(db_client=db_client, github_user_info=github_user_info)
        user_info_gh = db_client.get_user_info_by_external_account_id(
            external_account_id=str(github_user_info.user_id),
            external_account_type=ExternalAccountTypeEnum.GITHUB,
        )

    return login_response(
        user_info_gh,
        message=f"User with email {user_info_gh.email} created and logged in.",
    )
