"""
This module contains functions and helper functions
used by the `Search` resource
"""

import spacy
import json
import datetime
from typing import List, Dict, Any
from psycopg2.extensions import connection as PgConnection

# TODO: Create search_query_logs table to complement quick_search_query_logs


def expand_params(single_param: str, times: int):
    """
    Expand the single parameter a given number of times.
    Used for expanding parameters used repeatedly in SQL parameters
    :param single_param: The single parameter to be repeated multiple times.
    :param times: The number of times the single parameter should be repeated.
    :return: A tuple containing the repeated single_param.
    """
    return tuple([single_param] * times)


QUICK_SEARCH_COLUMNS = [
    "airtable_uid",
    "data_source_name",
    "description",
    "record_type",
    "source_url",
    "record_format",
    "coverage_start",
    "coverage_end",
    "agency_supplied",
    "agency_name",
    "municipality",
    "state_iso",
]

QUICK_SEARCH_SQL = """
    SELECT
        data_sources.airtable_uid,
        data_sources.name AS data_source_name,
        data_sources.description,
        data_sources.record_type,
        data_sources.source_url,
        data_sources.record_format,
        data_sources.coverage_start,
        data_sources.coverage_end,
        data_sources.agency_supplied,
        agencies.name AS agency_name,
        agencies.municipality,
        agencies.state_iso
    FROM
        agency_source_link
    INNER JOIN
        data_sources ON
            agency_source_link.airtable_uid = data_sources.airtable_uid
    INNER JOIN
        agencies ON
            agency_source_link.agency_described_linked_uid = agencies.airtable_uid
    INNER JOIN
        state_names ON
            agencies.state_iso = state_names.state_iso
    WHERE
        data_sources.record_type = ANY(%s) AND
        (
            agencies.county_name LIKE %s OR
            substr(agencies.county_name,3,length(agencies.county_name)-4)
                || ' County' LIKE %s
            OR agencies.state_iso LIKE %s
            OR agencies.municipality LIKE %s
            OR agencies.agency_type LIKE %s
            OR agencies.jurisdiction_type LIKE %s
            OR agencies.name LIKE %s
            OR state_names.state_name LIKE %s
        )
        AND data_sources.approval_status = 'approved'
        AND data_sources.url_status not in ('broken', 'none found')
"""

INSERT_LOG_QUERY = """
    INSERT INTO search_query_logs
    (search, location, results, result_count, created_at, datetime_of_request)
    VALUES (%s, %s, %s, %s, %s, %s)
"""


class SearchQueryEngine:
    """
    A search query engine to perform SQL queries
    for searching records based on a search term and location.
    """

    def __init__(self, connection: PgConnection):
        """
        Setup connection to PostgreSQL database and spacy nlp object
        :param connection: A PgConnection object
        """
        self.conn = connection
        self.nlp = spacy.load("en_core_web_sm")

    def execute_query(
        self, coarse_record_types: list[str], location: str
    ) -> List[Dict[str, Any]]:
        """
        Execute a SQL query to search for records
        based on a search term and location.

        :param search_term: The search term to query for.
        :param location: The location to search within.
        :return: A list of dictionaries containing the fetched records.
        """
        assert isinstance(
            coarse_record_types, list
        ), "coarse_record_types must be a list"
        with self.conn.cursor() as cursor:
            cursor.execute(
                QUICK_SEARCH_SQL, (coarse_record_types,) + expand_params(location, 8)
            )
            return cursor.fetchall()

    def print_query_parameters(self, search_terms: list[str], location: str) -> None:
        """
        :param search_terms: The search terms used in the query.
        :param location: The location used in the query.
        :return: None.
        """
        print(f"Query parameters: '%{search_terms}%', '%{location}%'")

    def lemmatize(self, entries: list[str]) -> list[str]:
        """
        Lemmatize all entries -- removing inflected forms to better enable searching
        :param entries: entries to be lemmatized
        :return: lemmatized results
        """
        lemmatized_terms = []
        for entry in entries:
            doc = self.nlp(entry.strip())
            lemmatized_term = " ".join([token.lemma_ for token in doc])
            lemmatized_terms.append(lemmatized_term)
        return lemmatized_terms

    def search_query(
        self, record_types: list[str], location: str
    ) -> List[Dict[str, Any]]:
        """
        Perform a search query based on the given parameters.

        :param record_types: The record types to search for.
        :param location: The location to search within.
        :return: A list of dictionaries,
            where each dictionary represents a search result.

        """
        self.print_query_parameters(record_types, location)
        results = self.execute_query(record_types, location)
        return results

    def quick_search(
        self,
        coarse_record_types: list[str] = None,
        location: str = "",
    ) -> Dict[str, Any]:
        """
        Perform a quick search based on the provided parameters.

        :param coarse_record_types: The types of records to search for.
        :param location: The location to search for records in.
        :param test: A flag indicating whether this is a test search.
        :return: A dictionary containing the search results.
        """
        unaltered_results = self.search_query(coarse_record_types, location)
        spacy_results = self.search_query(
            record_types=self.lemmatize(coarse_record_types), location=location
        )

        results = max(spacy_results, unaltered_results, key=len)
        data_sources = {"count": len(results), "data": results}

        self.log_query_results(coarse_record_types, location, data_sources)

        return data_sources

    def log_query_results(
        self,
        coarse_record_types: list[str],
        location: str,
        data_sources: Dict[str, Any],
    ) -> None:
        datetime_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # If both coarse_record_types and location are blank, all results will have been returned
        if len(coarse_record_types) > 0 or location != "":
            query_results = [record["airtable_uid"] for record in data_sources["data"]]
        else:
            query_results = ['ALL']
        with self.conn.cursor() as cursor:
            cursor.execute(
                INSERT_LOG_QUERY,
                (
                    coarse_record_types,
                    location,
                    json.dumps(query_results),
                    data_sources["count"],
                    datetime_string,
                ),
            )
            self.conn.commit()

