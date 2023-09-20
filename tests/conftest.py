import pandas as pd
import pandera as pa
import pytest

test_schema = pa.DataFrameSchema(
    {
        "column1": pa.Column(int, checks=pa.Check.le(10)),
        "column2": pa.Column(float, checks=pa.Check.lt(-1.2)),
        "column3": pa.Column(
            str,
            checks=[
                pa.Check.str_startswith("value_"),
                pa.Check(lambda s: s.str.split("_", expand=True).shape[1] == 2),
            ],
        ),
    }
)


@pytest.fixture(scope="module")
def df_empty() -> pd.DataFrame:
    return pd.DataFrame()


@pytest.fixture(scope="module")
def df_valid() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "column1": [1, 4, 0, 10, 9],
            "column2": [-1.3, -1.4, -2.9, -10.1, -20.4],
            "column3": ["value_1", "value_2", "value_3", "value_2", "value_1"],
        }
    )


@pytest.fixture(scope="module")
def df_invalid_values() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "column1": [11, 4, 0, 10, 1],
            "column2": [-1.3, -1.4, -2.9, -10.1, -20.4],
            "column3": ["value_1", "value_2", "value_3", "value_2", "value1"],
        }
    )


@pytest.fixture(scope="module")
def df_invalid_values_failure() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "schema_context": ["Column", "Column"],
            "column": ["column1", "column3"],
            "check": ["less_than_or_equal_to(10)", "str_startswith('value_')"],
            "check_number": [0, 0],
            "failure_case": [11, "value1"],
            "reference": [0, 4],
        }
    )


@pytest.fixture(scope="module")
def df_invalid_column() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "column1": [1, 4, 0, 10, 9],
            "column2": [-1.3, -1.4, -2.9, -10.1, -20.4],
            "column4": ["value_1", "value_2", "value_3", "value_2", "value_1"],
        }
    )


@pytest.fixture(scope="module")
def df_invalid_column_failure() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "schema_context": [
                "DataFrameSchema",
                "DataFrameSchema",
                "DataFrameSchema",
                "DataFrameSchema",
                "DataFrameSchema",
                "Column",
                "Column",
            ],
            "column": [
                "column2",
                "column2",
                "column2",
                "column2",
                "column2",
                "column1",
                "column3",
            ],
            "check": [
                "column_in_dataframe",
                "column_in_dataframe",
                "column_in_dataframe",
                "column_in_dataframe",
                "column_in_dataframe",
                "less_than_or_equal_to(10)",
                "str_startswith('value_')",
            ],
            "check_number": [
                None,
                None,
                None,
                None,
                None,
                0,
                0,
            ],
            "failure_case": [
                "column2",
                "column2",
                "column2",
                "column2",
                "column2",
                11,
                "value1",
            ],
            "reference": [
                0,
                1,
                2,
                3,
                4,
                0,
                4,
            ],
        }
    )
