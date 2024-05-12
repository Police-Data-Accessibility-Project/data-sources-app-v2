from werkzeug.security import generate_password_hash
from flask import request
from middleware.reset_token_queries import (
    check_reset_token,
    delete_reset_token,
)
from datetime import datetime as dt
from typing import Dict, Any

from resources.PsycopgResource import PsycopgResource
from utilities.managed_cursor import managed_cursor


class ResetPassword(PsycopgResource):
    """
    Provides a resource for users to reset their password using a valid reset token.
    If the token is valid and not expired, allows the user to set a new password.
    """

    def post(self) -> Dict[str, Any]:
        """
        Processes a password reset request. Validates the provided reset token and,
        if valid, updates the user's password with the new password provided in the request.

        Returns:
        - A dictionary containing a message indicating whether the password was successfully updated or an error occurred.
        """
        try:
            data = request.get_json()
            token = data.get("token")
            password = data.get("password")
            with managed_cursor(self.psycopg2_connection) as cursor:
                token_data = check_reset_token(cursor, token)
                email = token_data.get("email")
                if "create_date" not in token_data:
                    return {"message": "The submitted token is invalid"}, 400

                token_create_date = token_data["create_date"]
                token_expired = (dt.utcnow() - token_create_date).total_seconds() > 900
                delete_reset_token(cursor, token_data["email"], token)
                if token_expired:
                    return {"message": "The submitted token is invalid"}, 400

                password_digest = generate_password_hash(password)
                cursor.execute(
                    f"update users set password_digest = '{password_digest}' where email = '{email}'"
                )

            return {"message": "Successfully updated password"}

        except Exception as e:
            print(str(e))
            return {"message": str(e)}, 500
