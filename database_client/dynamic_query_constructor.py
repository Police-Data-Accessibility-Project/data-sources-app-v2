import uuid
from collections import namedtuple
from datetime import datetime
from typing import Optional

from psycopg2 import sql

from database_client.parameter_objects import AgencyDataSourceParams
from database_client.constants import (
    RESTRICTED_DATA_SOURCE_COLUMNS,
    AGENCY_DATA_SOURCE_VIEW_COLUMNS,
    DATA_SOURCES_NEEDS_IDENTIFICATION_COLUMNS,
)
from utilities.enums import RecordCategories

TableColumn = namedtuple("TableColumn", ["table", "column"])
TableColumnAlias = namedtuple("TableColumnAlias", ["table", "column", "alias"])


class DynamicQueryConstructor:
    """
    This is a class for constructing more complex queries
    where writing out the entire query is either impractical or unfeasible.
    Coupled with the DatabaseClient class, which utilizes the queries constructed here
    """

    @staticmethod
    def build_fields(
        columns_only: list[TableColumn],
        columns_and_alias: Optional[list[TableColumnAlias]] = None,
    ):
        # Process columns without alias
        fields_only = [
            sql.SQL("{}.{}").format(sql.Identifier(table), sql.Identifier(column))
            for table, column in columns_only
        ]

        if columns_and_alias:
            # Process columns with alias
            fields_with_alias = [
                sql.SQL("{}.{} AS {}").format(
                    sql.Identifier(col.table),
                    sql.Identifier(col.column),
                    sql.Identifier(col.alias),
                )
                for col in columns_and_alias
            ]
        else:
            fields_with_alias = []

        # Combine both lists
        all_fields = fields_only + fields_with_alias

        # Join fields to create the final fields SQL
        fields_sql = sql.SQL(", ").join(all_fields)

        return fields_sql

    @staticmethod
    def create_table_columns(table: str, columns: list[str]) -> list[TableColumn]:
        return [TableColumn(table, column) for column in columns]

    @staticmethod
    def build_needs_identification_data_source_query():
        data_sources_columns = DynamicQueryConstructor.create_table_columns(
            table="data_sources", columns=DATA_SOURCES_NEEDS_IDENTIFICATION_COLUMNS
        )
        fields = DynamicQueryConstructor.build_fields(
            columns_only=data_sources_columns,
        )
        sql_query = sql.SQL(
            """
            SELECT
                {fields}
            FROM
                data_sources
            WHERE
                approval_status = 'needs identification'
        """
        ).format(fields=fields)
        return sql_query

    @staticmethod
    def create_data_source_update_query(
        data: dict, data_source_id: str
    ) -> sql.Composed:
        """
        Creates a query to update a data source in the database.

        :param data: A dictionary containing the updated data source details.
        :param data_source_id: The ID of the data source to be updated.
        """
        data_to_update = []
        for key, value in data.items():
            if key in RESTRICTED_DATA_SOURCE_COLUMNS:
                continue
            data_to_update.append(
                sql.SQL("{} = {}").format(sql.Identifier(key), sql.Literal(value))
            )

        data_to_update_sql = sql.SQL(", ").join(data_to_update)

        query = sql.SQL(
            """
            UPDATE data_sources 
            SET {data_to_update}
            WHERE airtable_uid = {data_source_id}
        """
        ).format(
            data_to_update=data_to_update_sql,
            data_source_id=sql.Literal(data_source_id),
        )

        return query

    @staticmethod
    def create_new_data_source_query(data: dict) -> sql.Composed:
        """
        Creates a query to add a new data source to the database.

        :param data: A dictionary containing the data source details.
        """
        columns = []
        values = []
        for key, value in data.items():
            if key not in RESTRICTED_DATA_SOURCE_COLUMNS:
                columns.append(sql.Identifier(key))
                values.append(sql.Literal(value))

        now = datetime.now().strftime("%Y-%m-%d")
        airtable_uid = str(uuid.uuid4())

        columns.extend(
            [
                sql.Identifier("approval_status"),
                sql.Identifier("url_status"),
                sql.Identifier("data_source_created"),
                sql.Identifier("airtable_uid"),
            ]
        )
        values.extend(
            [
                sql.Literal(False),
                sql.Literal(["ok"]),
                sql.Literal(now),
                sql.Literal(airtable_uid),
            ]
        )

        query = sql.SQL("INSERT INTO data_sources ({}) VALUES ({}) RETURNING *").format(
            sql.SQL(", ").join(columns), sql.SQL(", ").join(values)
        )

        return query

    @staticmethod
    def generate_new_typeahead_suggestion_query(search_term: str):
        query = sql.SQL(
            """
        WITH combined AS (
            SELECT 
                1 AS sort_order,
                display_name,
                type,
                state,
                county,
                locality
            FROM typeahead_suggestions
            WHERE display_name ILIKE {search_term_prefix}
            UNION ALL
            SELECT
                2 AS sort_order,
                display_name,
                type,
                state,
                county,
                locality
            FROM typeahead_suggestions
            WHERE display_name ILIKE {search_term_anywhere}
            AND display_name NOT ILIKE {search_term_prefix}
        )
        SELECT DISTINCT 
            sort_order,
            display_name,
            type,
            state,
            county,
            locality
        FROM combined
        ORDER BY sort_order, display_name
        LIMIT 4;
        """
        ).format(
            search_term_prefix=sql.Literal(f"{search_term}%"),
            search_term_anywhere=sql.Literal(f"%{search_term}%"),
        )
        return query

    @staticmethod
    def create_search_query(
        state: str,
        record_type: Optional[RecordCategories] = None,
        county: Optional[str] = None,
        locality: Optional[str] = None,
    ) -> sql.Composed:

        base_query = sql.SQL(
            """
            SELECT
                adsv.data_source_id as airtable_uid,
                adsv.data_source_name,
                adsv.description,
                adsv.record_type,
                adsv.source_url,
                adsv.record_format,
                adsv.coverage_start,
                adsv.coverage_end,
                adsv.agency_supplied,
                adsv.agency_name,
                adsv.municipality,
                adsv.state_iso
            FROM
                agency_data_source_view adsv
            INNER JOIN
                state_names ON adsv.state_iso = state_names.state_iso
            INNER JOIN
                counties ON adsv.county_fips = counties.fips
        """
        )

        join_conditions = []
        where_conditions = [
            sql.SQL("state_names.state_name = {state_name}").format(
                state_name=sql.Literal(state)
            ),
            sql.SQL("adsv.approval_status = 'approved'"),
            sql.SQL("adsv.url_status NOT IN ('broken', 'none found')"),
        ]

        if record_type is not None:
            join_conditions.append(
                sql.SQL(
                    """
                INNER JOIN
                    record_types ON adsv.record_type_id = record_types.id
                INNER JOIN
                    record_categories ON record_types.category_id = record_categories.id
            """
                )
            )

            DynamicQueryConstructor.add_condition(where_conditions, "name", record_type.value, "record_categories")

        DynamicQueryConstructor.add_condition(where_conditions, "name", county, "counties")
        DynamicQueryConstructor.add_condition(where_conditions, "municipality", locality, "adsv")

        query = sql.Composed(
            [
                base_query,
                sql.SQL(" ").join(join_conditions),
                sql.SQL(" WHERE "),
                sql.SQL(" AND ").join(where_conditions),
            ]
        )

        return query

    @staticmethod
    def add_condition(conditions: list, column: str, value: str, table_name: Optional[str] = None):
        if value is None:
            return
        if table_name is not None:
            conditions.append(sql.SQL("{}.{} = {}").format(
                sql.Identifier(table_name),
                sql.Identifier(column),
                sql.Literal(value)))
        else:
            conditions.append(sql.SQL("{} = {}").format(
                sql.Identifier(column),
                sql.Literal(value)))

    @staticmethod
    def add_limit_offset_clause(clause, value, clause_type):
        if value is None:
            return sql.SQL("")
        if clause_type == "OFFSET":
            return sql.SQL(" OFFSET {}").format(
                sql.Literal(value))
        elif clause_type == "LIMIT":
            return sql.SQL(" LIMIT {}").format(
                sql.Literal(value))

    @staticmethod
    def handle_select_columns(include_columns, exclude_columns):
        if include_columns is not None:
            return [sql.Identifier(col) for col in include_columns]
        elif exclude_columns is not None:
            exclude_columns_set = set(exclude_columns)
            return [
                sql.Identifier(col)
                for col in set(AGENCY_DATA_SOURCE_VIEW_COLUMNS) - exclude_columns_set
            ]
        else:
            return [sql.Identifier(col) for col in AGENCY_DATA_SOURCE_VIEW_COLUMNS]

    @staticmethod
    def build_agency_data_source_query(params: AgencyDataSourceParams):
        base_query = sql.SQL(
            """
            SELECT
                {columns}
            FROM 
                agency_data_source_view
            """
        )

        # Dynamically add WHERE clauses
        conditions = []
        DynamicQueryConstructor.add_condition(conditions, "agency_id", params.agency_id)
        DynamicQueryConstructor.add_condition(conditions, "data_source_id", params.data_source_id)
        DynamicQueryConstructor.add_condition(conditions, "approval_status", params.approval_status)

        where_clause = sql.SQL(" WHERE ") + sql.SQL(" AND ").join(conditions) if conditions else sql.SQL("")

        # Add LIMIT and OFFSET clauses if applicable
        limit_clause = DynamicQueryConstructor.add_limit_offset_clause(sql.SQL(""), params.limit, "LIMIT")
        offset_clause = DynamicQueryConstructor.add_limit_offset_clause(sql.SQL(""), params.offset, "OFFSET")

        # Handle optional columns
        select_columns = DynamicQueryConstructor.handle_select_columns(params.include_columns, params.exclude_columns)

        # Combine everything together
        final_query = (
            base_query.format(columns=sql.SQL(", ").join(select_columns))
            + where_clause
            + limit_clause
            + offset_clause
        )

        return final_query
