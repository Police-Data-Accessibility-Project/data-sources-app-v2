import json
from unittest.mock import patch
from conftest import test_client, session

import pytest

from middleware.database_enums import RecordType


@pytest.fixture
def mock_request_info():
    return {
        'submission_notes': 'Test notes',
        'submitter_contact_info': 'contact@example.com',
        'submitter_user_id': 'user123',
        'agency_described_submitted': 'Agency',
        'record_type': RecordType.ARREST_RECORDS.value
    }


# @patch('app.db.session.add')
# @patch('app.db.session.commit')
def test_post_request(test_client, mock_request_info, session):
    response = test_client.post(
        '/data-request',
        data=json.dumps(mock_request_info),
        content_type='application/json'
    )
    assert response.status_code == 201
    assert response.json['message'] == 'Created successfully'
