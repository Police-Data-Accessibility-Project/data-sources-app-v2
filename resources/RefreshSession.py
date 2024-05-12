from flask import request
from middleware.login_queries import token_results, create_session_token
from datetime import datetime as dt
from typing import Dict, Any

from resources.PsycopgResource import PsycopgResource
from utilities.managed_cursor import managed_cursor


class RefreshSession(PsycopgResource):
    """
    Provides a resource for refreshing a user's session token.
    If the provided session token is valid and not expired, it is replaced with a new one.
    """

    def post(self) -> Dict[str, Any]:
        """
        Processes the session token refresh request. If the provided session token is valid,
        it generates a new session token, invalidates the old one, and returns the new token.

        Returns:
        - A dictionary containing a message of success or failure, and the new session token if successful.
        """
        try:
            data = request.get_json()
            old_token = data.get("session_token")
            with managed_cursor(self.psycopg2_connection) as cursor:
                user_data = token_results(cursor, old_token)
                cursor.execute(
                    f"delete from session_tokens where token = '{old_token}' and expiration_date < '{dt.utcnow()}'"
                )

                if "id" not in user_data:
                    return {"message": "Invalid session token"}, 403

                token = create_session_token(
                    cursor, user_data["id"], user_data["email"]
                )
                return {
                    "message": "Successfully refreshed session token",
                    "data": token,
                }

        except Exception as e:
            print(str(e))
            return {"message": str(e)}, 500
