import os

import dotenv
import pytest
from middleware.models import db

from app import create_app


# Load environment variables
dotenv.load_dotenv()

@pytest.fixture(scope="module")
def test_client():
    app = create_app()
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DEV_DB_CONN_STRING")  # Connect to pre-existing test database
    app.config["TESTING"] = True

    db.init_app(app)

    with app.test_client() as testing_client:
        with app.app_context():
            yield testing_client

@pytest.fixture
def session(test_client):
    with test_client.application.app_context():
        yield db.session
        db.session.rollback()  # Rollback any changes made during the test
        db.session.close()
