import psycopg2
from psycopg2 import sql
from dataclasses import dataclass

from middleware.database_enums import RecordType, RequestStatus
from utilities.DBRequestMapper import DBRequestMapper


@dataclass
class RequestInfo(DBRequestMapper):
    submission_notes: str
    submitter_contact_info: str
    submitter_user_id: str
    agency_described_submitted: str
    record_type: RecordType

REQUESTS_TABLE = "requests_v2"

@dataclass
class UpdateableRequestColumns(DBRequestMapper):
    submission_notes: str
    submitter_contact_info: str
    submitter_user_id: str
    agency_described_submitted: str
    record_type: RecordType
    archive_reason: str
    github_issue_url: str
    request_status: RequestStatus


class DataRequestsManager:
    """
    This class manages CRUD operations for the 'data_requests' table in a PostgreSQL database.
    It requires a psycopg2 connection object to interact with the database.

    Attributes:
        conn (psycopg2.connect): A psycopg2 connection object to the PostgreSQL database.
    """

    def create_request(
            self,
            cursor: psycopg2.extensions.cursor,
            request_info: RequestInfo
    ) -> int:
        """
        Creates a new entry in the data_requests table.

        Parameters:
            :param cursor:
            :param request_info: Information on the request, to be inserted into the data_requests table

        Returns:
            int: The id of the newly created record.
        """
        insert_query = request_info.create_insert_query(
            table_name=REQUESTS_TABLE
        )
        cursor.execute(
            insert_query.query, insert_query.values
        )
        return cursor.fetchone()[0]

    def read_request(self, request_id: int) -> tuple:
        """
        Reads a specific entry from the data_requests table.

        Parameters:
            request_id (int): The ID of the request to retrieve.

        Returns:
            tuple: All columns of the entry as a tuple.
        """
        with self.conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {REQUESTS_TABLE} WHERE id = %s;", (request_id,)
            )
            return cur.fetchone()

    def update_request(
        self,
        cursor: psycopg2.extensions.cursor,
        request_id: str,
        updateable_request_columns: UpdateableRequestColumns,
    ) -> None:
        """
        Updates specified fields of an existing entry in the data_requests table.

        Parameters:
            request_id (int): The ID of the request to update.
            **kwargs: Variable keyword arguments corresponding to column names and their new values.
            :param request_id:
            :param cursor:
            :param updateable_request_columns:
        """
        update_subquery = updateable_request_columns.create_update_query(
            table_name=REQUESTS_TABLE,
            where_column="id",
            id_value=request_id
        )
        cursor.execute(update_subquery.query, update_subquery.values)


    def delete_request(self, request_id: int) -> int:
        """
        Deletes a specific entry from the data_requests table.

        Parameters:
            request_id (int): The ID of the request to delete.
        """
        with self.conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM {REQUESTS_TABLE} WHERE id = %s;", (request_id,)
            )
            self.conn.commit()
