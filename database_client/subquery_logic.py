from dataclasses import dataclass
from functools import partialmethod

from sqlalchemy.orm import defaultload
from sqlalchemy.sql.base import ExecutableOption

from database_client.models import convert_to_column_reference
from middleware.enums import Relations


@dataclass
class SubqueryParameters:
    """
    Contains parameters for executing a subquery
    """

    relation_name: str
    linking_column: str
    columns: list[str] = None

    def set_columns(self, columns: list[str]) -> None:
        self.columns = columns

    def build_subquery_load_option(self, primary_relation: str) -> ExecutableOption:
        """Creates a SQLAlchemy ExecutableOption for subquerying.

        :param primary_relation:
        :return: ExecutableOption. Example: defaultload(DataSource.agencies).load_only(Agency.name)
        """
        column_references = convert_to_column_reference(
            columns=self.columns, relation=self.relation_name
        )
        linking_column_reference = convert_to_column_reference(
            columns=[self.linking_column], relation=primary_relation
        )

        return defaultload(*linking_column_reference).load_only(*column_references)


class SubqueryParameterManager:
    """
    Consolidates and manages the retrieval of subquery parameters
    """
    @staticmethod
    def get_subquery_params(
            relation: Relations,
            linking_column: str,
            columns: list[str] = None
    ) -> SubqueryParameters:
        return SubqueryParameters(
            relation_name=relation.value,
            linking_column=linking_column,
            columns=columns
        )

    agencies = partialmethod(
        get_subquery_params,
        relation=Relations.AGENCIES_EXPANDED,
        linking_column="agencies",
    )

    data_sources = partialmethod(
        get_subquery_params,
        relation=Relations.DATA_SOURCES_EXPANDED,
        linking_column="data_sources",
        columns=["airtable_uid", "submitted_name"],
    )