import functools
from collections import namedtuple

from flask import request, jsonify
from middleware.initialize_psycopg2_connection import initialize_psycopg2_connection
from datetime import datetime as dt
from middleware.login_queries import is_admin
from middleware.custom_exceptions import UserNotFoundError
from typing import Tuple

APIKeyStatus = namedtuple("APIKeyStatus", ["is_valid", "is_expired"])


def is_valid(api_key: str, endpoint: str, method: str) -> APIKeyStatus:
    """
    Validates the API key and checks if the user has the required role to access a specific endpoint.

    :param api_key: The API key provided by the user.
    :param endpoint: The endpoint the user is trying to access.
    :param method: The HTTP method of the request.
    :return: A tuple (isValid, isExpired) indicating whether the API key is valid and not expired.
    """
    if not api_key:
        return APIKeyStatus(is_valid=False, is_expired=False)

    session_token_results = None
    psycopg2_connection = initialize_psycopg2_connection()
    cursor = psycopg2_connection.cursor()
    role = get_role(api_key, cursor)
    if role is None:
        session_token_results = get_session_token(
            api_key, cursor, session_token_results
        )
        if len(session_token_results) > 0:
            email = session_token_results[0][0]
            expiration_date = session_token_results[0][1]
            print(expiration_date, dt.utcnow())

            if expiration_date < dt.utcnow():
                return APIKeyStatus(False, is_expired=True)

            if is_admin(cursor, email):
                role = "admin"

    if not session_token_results and role is None:
        delete_expired_access_tokens(cursor, psycopg2_connection)
        access_token = get_access_token(api_key, cursor)
        role = "user"

        if not access_token:
            return APIKeyStatus(is_valid=False, is_expired=False)

    if is_admin_only_action(endpoint, method) and role != "admin":
        return APIKeyStatus(is_valid=False, is_expired=False)

    # Compare the API key in the user table to the API in the request header and proceed
    # through the protected route if it's valid. Otherwise, compare_digest will return False
    # and api_required will send an error message to provide a valid API key
    return APIKeyStatus(is_valid=True, is_expired=False)


def get_role(api_key, cursor):
    cursor.execute(f"select id, api_key, role from users where api_key = '{api_key}'")
    user_results = cursor.fetchall()
    if len(user_results) > 0:
        role = user_results[0][2]
        if role is None:
            return "user"
        return role
    return None


def get_session_token(api_key, cursor, session_token_results):
    cursor.execute(
        f"select email, expiration_date from session_tokens where token = '{api_key}'"
    )
    session_token_results = cursor.fetchall()
    return session_token_results


def get_access_token(api_key, cursor):
    cursor.execute(f"select id, token from access_tokens where token = '{api_key}'")
    results = cursor.fetchone()
    if results:
        return results[1]
    return None


def delete_expired_access_tokens(cursor, psycopg2_connection):
    cursor.execute(f"delete from access_tokens where expiration_date < '{dt.utcnow()}'")
    psycopg2_connection.commit()


def is_admin_only_action(endpoint, method):
    return endpoint in ("datasources", "datasourcebyid") and method in ("PUT", "POST")


def api_required(func):
    """
    The api_required decorator can be added to protect a route so that only authenticated users can access the information
    To protect a route with this decorator, add @api_required on the line above a given route
    The request header for a protected route must include an "Authorization" key with the value formatted as "Bearer [api_key]"
    A user can get an API key by signing up and logging in (see User.py)
    """

    @functools.wraps(func)
    def decorator(*args, **kwargs):
        api_key = None
        if request.headers and "Authorization" in request.headers:
            authorization_header = request.headers["Authorization"].split(" ")
            if len(authorization_header) >= 2 and authorization_header[0] == "Bearer":
                api_key = request.headers["Authorization"].split(" ")[1]
                if api_key == "undefined":
                    return {"message": "Please provide an API key"}, 400
            else:
                return {
                    "message": "Please provide a properly formatted bearer token and API key"
                }, 400
        else:
            return {
                "message": "Please provide an 'Authorization' key in the request header"
            }, 400
        # Check if API key is correct and valid
        try:
            api_key_status = is_valid(api_key, request.endpoint, request.method)
        except UserNotFoundError as e:
            return {"message": str(e)}, 401
        if api_key_status.is_valid:
            return func(*args, **kwargs)
        else:
            if api_key_status.is_expired:
                return {"message": "The provided API key has expired"}, 401
            return {"message": "The provided API key is not valid"}, 403

    return decorator
