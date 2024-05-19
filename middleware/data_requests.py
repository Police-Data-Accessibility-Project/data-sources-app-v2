from app import db
from middleware.database_enums import RecordType, RequestStatus

class RequestInfo(db.Model):
    __tablename__ = "requests_v2"
    id = db.Column(db.Integer, primary_key=True)
    submission_notes = db.Column(db.String)
    submitter_contact_info = db.Column(db.String)
    submitter_user_id = db.Column(db.String)
    agency_described_submitted = db.Column(db.String)
    record_type = db.Column(db.Enum(RecordType))
    archive_reason = db.Column(db.String, nullable=True)
    github_issue_url = db.Column(db.String, nullable=True)
    request_status = db.Column(db.Enum(RequestStatus), nullable=True)