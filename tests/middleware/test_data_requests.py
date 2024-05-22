import json
from conftest import test_client, session

import pytest

from middleware.database_enums import RecordType
from middleware.models import RequestV2, request_status_enum
from tests.middleware.helper_functions import (
    create_test_user_sqlalchemy,
    generate_secure_random_alphanumeric,
    create_test_request_sqlalchemy,
)


@pytest.fixture
def mock_request_info():
    return {
        "submission_notes": generate_secure_random_alphanumeric(20),
        "submitter_contact_info": generate_secure_random_alphanumeric(15),
        "agency_described_submitted": generate_secure_random_alphanumeric(20),
        "record_type": "Dispatch Recordings",
    }


def process_post_request(test_client, mock_request_info, session, user_id=None):
    """
    Process a POST request using the provided test_client, mock_request_info, session, and user_id.
    If a user_id is provided, the user_id is included in the mock_request
        and its presence tested in the requests_v2 result

    :param test_client: The test_client object used for making HTTP requests.
    :param mock_request_info: The mock request information to be sent in the POST request.
    :param session: The session object used for querying the database.
    :param user_id: The ID of the user making the POST request. Defaults to None.
    """
    mock_request_info["submitter_user_id"] = str(user_id) if user_id else None
    response = test_client.post(
        "/data-request",
        data=json.dumps(mock_request_info),
        content_type="application/json",
    )
    assert response.status_code == 201

    filter_args = (
        {"submitter_user_id": user_id}
        if user_id
        else {"submitter_contact_info": mock_request_info["submitter_contact_info"]}
    )
    data_request = session.query(RequestV2).filter_by(**filter_args).first()

    assert response.json["message"] == "Created successfully"
    assert data_request.record_type == "Dispatch Recordings"
    assert data_request.submitter_user_id == user_id
    assert (
        data_request.agency_described_submitted
        == mock_request_info["agency_described_submitted"]
    )
    assert data_request.submission_notes == mock_request_info["submission_notes"]
    assert (
        data_request.submitter_contact_info
        == mock_request_info["submitter_contact_info"]
    )
    assert data_request.request_status == "Intake"


def test_post_request_no_user(test_client, mock_request_info, session):
    """
    Test post request from a nonuser
    :param test_client:
    :param mock_request_info:
    :param session:
    :return:
    """
    user = create_test_user_sqlalchemy(session)
    process_post_request(test_client, mock_request_info, session)


def test_post_request_user(test_client, mock_request_info, session):
    """
    Test post request with an existing user
    :param test_client:
    :param mock_request_info:
    :param session:
    :return:
    """
    user = create_test_user_sqlalchemy(session)
    process_post_request(test_client, mock_request_info, session, user.id)


def test_delete_request(test_client, session):
    """
    Test a created request is successfully deleted by the DELETE endpoint
    :param test_client:
    :param session:
    :return:
    """
    data_request = create_test_request_sqlalchemy(session)
    assert session.get(RequestV2, data_request.id)
    response = test_client.delete(
        "/data-request",
        data=json.dumps({"request_id": data_request.id}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.json["message"] == "Deleted successfully"
    assert session.query(RequestV2).get(data_request.id) is None

def test_get_request(test_client, session):
    """
    Test a created request is successfully retrieved by the GET endpoint
    :param test_client:
    :param session:
    :return:
    """
    data_request = create_test_request_sqlalchemy(session)
    assert session.get(RequestV2, data_request.id)
    response = test_client.get(
        "/data-request",
        data=json.dumps({"request_id": data_request.id}),
        content_type="application/json",
    )
    assert response.json["data"]["id"] == data_request.id