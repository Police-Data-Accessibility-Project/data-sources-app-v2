from flask import request
from flask_restful import Resource
from middleware.models import db
from middleware.data_requests import RequestInfo
from middleware.security import api_required
from resources.PsycopgResource import handle_exceptions
from utilities.common import str_to_enum
from middleware.database_enums import RecordType



class DataRequest(Resource):
    """
    Flask-Restful resource for handling CRUD operations on the 'requests_v2' table.
    Uses Flask-SQLAlchemy for database interactions.
    """

    # @api_required
    # @handle_exceptions
    def post(self) -> tuple[dict, int]:
        """
        Handles the creation of a new data request.
        Expects 'submission_notes' and 'submitter_contact_info' in the request body.
        """
        data = request.json
        request_info = RequestInfo(
            submission_notes=data.get("submission_notes"),
            submitter_contact_info=data.get("submitter_contact_info"),
            submitter_user_id=data.get("submitter_user_id"),
            agency_described_submitted=data.get("agency_described_submitted"),
            record_type=str_to_enum(RecordType, data.get("record_type")),
        )
        db.session.add(request_info)
        db.session.commit()
        return {"message": "Created successfully", "id": request_info.id}, 201

    # @api_required
    # @handle_exceptions
    def get(self) -> tuple[dict, int]:
        """
        Retrieves a data request by ID.
        """
        request_id = request.json["request_id"]
        request_info = RequestInfo.query.get(request_id)
        if request_info:
            return {"data": request_info.__dict__}, 200
        else:
            return {"message": "Data request not found"}, 404

    # @api_required
    # @handle_exceptions
    def put(self) -> tuple[dict, int]:
        """
        Updates an existing data request.
        Expects any of the updatable fields in the request body.
        """
        request_id = request.json["request_id"]
        request_info = RequestInfo.query.get(request_id)
        if not request_info:
            return {"message": "Data request not found"}, 404

        data = request.json
        request_info.submission_notes = data.get(
            "submission_notes", request_info.submission_notes
        )
        request_info.submitter_contact_info = data.get(
            "submitter_contact_info", request_info.submitter_contact_info
        )
        request_info.submitter_user_id = data.get(
            "submitter_user_id", request_info.submitter_user_id
        )
        request_info.agency_described_submitted = data.get(
            "agency_described_submitted", request_info.agency_described_submitted
        )
        request_info.record_type = str_to_enum(
            RecordType, data.get("record_type", request_info.record_type)
        )
        db.session.commit()
        return {"message": "Updated successfully"}, 200

    # @api_required
    # @handle_exceptions
    def delete(self) -> tuple[dict, int]:
        """
        Deletes a data request by ID.
        """
        request_id = request.json["request_id"]
        request_info = RequestInfo.query.get(request_id)
        if request_info:
            db.session.delete(request_info)
            db.session.commit()
            return {"message": "Deleted successfully"}, 200
        else:
            return {"message": "Data request not found"}, 404
