import datetime

import sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Column,
    BigInteger,
    text,
    Text,
    String,
    CheckConstraint,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship

db = SQLAlchemy()

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    email = Column(Text, nullable=False, unique=True)
    password_digest = Column(Text)
    api_key = Column(String)
    role = Column(Text)

    # Relationships
    requests_v2 = relationship("RequestV2", back_populates="submitter_user")


request_status_enum = ENUM(
    "Intake",
    "Active",
    "Complete",
    "Request withdrawn",
    "Waiting for scraper",
    "Archived",
    name="request_status",
    create_type=False,
)

record_type_enum = ENUM(
    "Dispatch Recordings",
    "Arrest Records",
    "Citations",
    "Incarceration Records",
    "Booking Reports",
    "Budgets & Finances",
    "Misc Police Activity",
    "Geographic",
    "Crime Maps & Reports",
    "Other",
    "Annual & Monthly Reports",
    "Resources",
    "Dispatch Logs",
    "Sex Offender Registry",
    "Officer Involved Shootings",
    "Daily Activity Logs",
    "Crime Statistics",
    "Records Request Info",
    "Policies & Contracts",
    "Stops",
    "Media Bulletins",
    "Training & Hiring Info",
    "Personnel Records",
    "Contact Info & Agency Meta",
    "Incident Reports",
    "Calls for Service",
    "Accident Reports",
    "Use of Force Reports",
    "Complaints & Misconduct",
    "Vehicle Pursuits",
    "Court Cases",
    "Surveys",
    "Field Contacts",
    "Wanted Persons",
    "List of Data Sources",
    name="record_type",
    create_type=False,
)


class RequestV2(Base):
    __tablename__ = "requests_v2"
    __table_args__ = (
        CheckConstraint(
            "(github_issue_url IS NULL OR github_issue_url ~* '^https?://[^\s/$.?#].[^\s]*$'::text)",
            name="requests_v2_github_issue_url_check",
        ),
        {"schema": "public"},
    )

    id = Column(
        BigInteger,
        primary_key=True,
        server_default=text("nextval('requests_v2_id_seq'::regclass)"),
    )
    submission_notes = Column(Text, nullable=False)
    request_status = Column(
        request_status_enum,
        nullable=False,
        server_default=text("'Intake'::request_status"),
    )
    submitter_contact_info = Column(Text)
    submitter_user_id = Column(BigInteger, ForeignKey("public.users.id"))
    agency_described_submitted = Column(Text)
    record_type = Column(record_type_enum)
    archive_reason = Column(Text)
    date_created = Column(TIMESTAMP, nullable=False, server_default=text("now()"))
    date_status_last_changed = Column(
        TIMESTAMP, nullable=False, server_default=text("now()")
    )
    github_issue_url = Column(Text)

    # Relationships (if needed)
    submitter_user = relationship("User", back_populates="requests_v2")

    def to_dict(self):
        result = {}
        for c in sqlalchemy.inspect(self).mapper.column_attrs:
            value = getattr(self, c.key)
            if isinstance(value, datetime.datetime):
                value = value.isoformat()
            result[c.key] = value
        return result
