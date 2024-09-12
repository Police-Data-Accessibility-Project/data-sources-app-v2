from dataclasses import dataclass

from marshmallow import Schema, fields
from werkzeug.security import generate_password_hash
from typing import Dict

from database_client.database_client import DatabaseClient
from middleware.exceptions import UserNotFoundError
from utilities.enums import SourceMappingEnum


class UserRequestSchema(Schema):
    email = fields.Str(
        required=True,
        metadata={
            "description": "The email of the user",
            "source": SourceMappingEnum.JSON
        }
    )
    password = fields.Str(
        required=True,
        metadata={
            "description": "The password of the user",
            "source": SourceMappingEnum.JSON
        }
    )

@dataclass
class UserRequest:
    email: str
    password: str



def user_check_email(db_client: DatabaseClient, email: str) -> None:
    """
    Checks if a user with the given email exists in the database, raising an error if not.

    :param db_client: A DatabaseClient object.
    :param email: The email address to check against the users in the database.
    :return: A dictionary with the user's ID if found, otherwise an error message.
    """
    user_id = db_client.get_user_id(email)
    if user_id is None:
        raise UserNotFoundError(email)


def user_post_results(db_client: DatabaseClient, dto: UserRequest) -> None:
    """
    Creates a new user with the provided email and password.

    :param db_client: A DatabaseClient object.
    :param email: The email address of the new user.
    :param password: The password for the new user.
    """
    password_digest = generate_password_hash(dto.password)
    db_client.add_new_user(dto.email, password_digest)
