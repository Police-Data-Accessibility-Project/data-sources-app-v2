"""
This file contains the parameter objects used by the DatabaseClient class.

"""



from typing import Optional, List, Any

class AgencyDataSourceParams:
    def __init__(
        self,
        agency_id: Optional[str] = None,
        data_source_id: Optional[str] = None,
        include_columns: Optional[List[str]] = None,
        exclude_columns: Optional[List[str]] = None,
        approval_status: Optional[str] = 'approved',
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ):
        self.agency_id = agency_id
        self.data_source_id = data_source_id
        self.include_columns = include_columns
        self.exclude_columns = exclude_columns
        self.approval_status = approval_status
        self.limit = limit
        self.offset = offset
        self._validate()

    def _validate(self):
        if self.include_columns is not None and self.exclude_columns is not None:
            raise ValueError("include_columns and exclude_columns cannot both be not-None at the same time.")