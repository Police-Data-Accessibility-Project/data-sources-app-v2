from collections import namedtuple
from typing import Any

from psycopg2.extras import DictRow

from utilities.common import convert_dates_to_strings, format_arrays

class ResultFormatter:
    """
    Formats results for specific database queries
    Coupled with the DatabaseClient class, whose outputs are formatted here
    """

    @staticmethod
    def convert_data_source_matches(
        results: list[DictRow]
    ) -> list[dict]:
        """
        Combine a list of output columns with a list of results,
        and produce a list of dictionaries where the keys correspond
        to the output columns and the values correspond to the results
        :param results:
        :return:
        """
        columns = list(results[0].keys())
        data_source_matches = [
            dict(zip(columns, result)) for result in results
        ]
        data_source_matches_converted = []
        for data_source_match in data_source_matches:
            data_source_match = convert_dates_to_strings(data_source_match)
            data_source_matches_converted.append(format_arrays(data_source_match))
        return data_source_matches_converted

    @staticmethod
    def zip_get_data_source_by_id_results(result: DictRow[Any, ...]) -> dict[str, Any]:
        return ResultFormatter.convert_data_source_matches([result])[0]

def dictify_namedtuple(result: list[namedtuple]) -> list[dict[str, Any]]:
    return [result._asdict() for result in result]