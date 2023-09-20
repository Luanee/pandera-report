import pytest

from pandera_report.parser import DefaultFailureCaseParser


def test_default_failure_case_parser_valid_dataframe(df_empty):
    parser = DefaultFailureCaseParser()

    series_issues, series_status = parser.parse_failure_cases(df_empty, len(df_empty))

    assert (series_issues == "None").all()
    assert (series_status == "Valid").all()


def test_default_failure_case_parser_invalid_dataframe_values(df_invalid_values, df_invalid_values_failure):
    parser = DefaultFailureCaseParser()

    series_issues, series_status = parser.parse_failure_cases(df_invalid_values_failure, len(df_invalid_values))

    assert (
        series_issues
        == [
            "Column <column1>: less_than_or_equal_to(10)",
            "None",
            "None",
            "None",
            "Column <column3>: str_startswith('value_')",
        ]
    ).all()
    assert (
        series_status
        == [
            "Invalid",
            "Valid",
            "Valid",
            "Valid",
            "Invalid",
        ]
    ).all()


def test_default_failure_case_parser_invalid_dataframe_columns(df_invalid_column, df_invalid_column_failure):
    parser = DefaultFailureCaseParser()

    series_issues, series_status = parser.parse_failure_cases(df_invalid_column_failure, len(df_invalid_column))

    assert (
        series_issues
        == [
            "Column <column2>: column_in_dataframe | Column <column1>: less_than_or_equal_to(10)",
            "Column <column2>: column_in_dataframe",
            "Column <column2>: column_in_dataframe",
            "Column <column2>: column_in_dataframe",
            "Column <column2>: column_in_dataframe | Column <column3>: str_startswith('value_')",
        ]
    ).all()
    assert (
        series_status
        == [
            "Invalid",
            "Invalid",
            "Invalid",
            "Invalid",
            "Invalid",
        ]
    ).all()
