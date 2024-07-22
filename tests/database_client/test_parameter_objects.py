import pytest

from database_client.parameter_objects import AgencyDataSourceParams


def test_agency_data_source_params_validate():
    """
    Test that the AgencyDataSourceParams class raises a ValueError if both
    include_columns and exclude_columns are not None
    :return:
    """
    with pytest.raises(ValueError):
        AgencyDataSourceParams(
            include_columns=["test_column_1"],
            exclude_columns=["test_column_2"],
        )