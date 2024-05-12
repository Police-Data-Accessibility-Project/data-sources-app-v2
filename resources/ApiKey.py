from werkzeug.security import check_password_hash
from flask import request
from middleware.login_queries import login_results
import uuid
from typing import Dict, Any, Optional

from resources.PsycopgResource import PsycopgResource
from utilities.managed_cursor import managed_cursor


class ApiKey(PsycopgResource):
    """Represents a resource for generating an API key for authenticated users."""

    def get(self) -> Optional[Dict[str, Any]]:
        """
        Authenticates a user based on provided credentials and generates an API key.

        Reads the 'email' and 'password' from the JSON body of the request, validates the user,
        and if successful, generates and returns a new API key.

        Returns:
        - dict: A dictionary containing the generated API key, or None if an error occurs.
        """
        try:
            data = request.get_json()
            email = data.get("email")
            password = data.get("password")

            with managed_cursor(self.psycopg2_connection) as cursor:
                user_data = login_results(cursor, email)

                if not check_password_hash(user_data["password_digest"], password):
                    return
                api_key = uuid.uuid4().hex
                user_id = str(user_data["id"])
                cursor.execute(
                    "UPDATE users SET api_key = %s WHERE id = %s", (api_key, user_id)
                )
            payload = {"api_key": api_key}
            return payload

        except Exception as e:
            print(str(e))
            return {"message": str(e)}
