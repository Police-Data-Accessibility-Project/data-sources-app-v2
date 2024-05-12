from werkzeug.security import check_password_hash
from flask import request
from middleware.login_queries import login_results, create_session_token
from resources.PsycopgResource import PsycopgResource
from utilities.managed_cursor import managed_cursor


class Login(PsycopgResource):
    """
    A resource for authenticating users. Allows users to log in using their email and password.
    """

    def post(self):
        """
        Processes the login request. Validates user credentials against the stored hashed password and,
        if successful, generates a session token for the user.

        Returns:
        - A dictionary containing a message of success or failure, and the session token if successful.
        """
        try:
            data = request.get_json()
            email = data.get("email")
            password = data.get("password")

            with managed_cursor(self.psycopg2_connection) as cursor:
                user_data = login_results(cursor, email)

                if "password_digest" not in user_data or not check_password_hash(
                        user_data["password_digest"], password
                ):
                    return {"message": "Invalid email or password"}, 401

                token = create_session_token(cursor, user_data["id"], email)
            return {
                "message": "Successfully logged in",
                "data": token,
            }

        except Exception as e:
            print(str(e))
            return {"message": str(e)}, 500
