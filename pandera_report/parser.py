import abc
from typing import Optional, Protocol

import numpy as np
import pandas as pd

from .options import QUALITY_STATUS_OPTIONS, QualityStatusOptions


class FailureCaseParser(Protocol):
    """
    An abstract base class for pandera's failure cases dataframe.

    This class defines the basic structure and properties of failure case parsers.
    """

    # pylint: disable=missing-function-docstring
    @abc.abstractmethod
    def parse_failure_cases(self, df: pd.DataFrame, number_of_rows: int) -> tuple[pd.Series, pd.Series]:
        ...

    @abc.abstractmethod
    def create_quality_issues_series(self, df: pd.DataFrame) -> pd.Series:
        ...

    @abc.abstractmethod
    def create_quality_status_series(self, series_issues: pd.Series) -> pd.Series:
        ...

    @abc.abstractmethod
    def create_failure_case(self, column: str, check: str) -> str:
        ...

    # pylint: enable=missing-function-docstring


class DefaultFailureCaseParser(FailureCaseParser):
    """
    A default implementation of the FailureCaseParser abstract class.
    Parses failure cases from a DataFrame and creates corresponding quality issues and status series.

    Parameters:
        status (Optional[QualityStatusOptions]): Optional. The quality status options to use.
            If not provided, the default quality status options are used.

    Attributes:
        _valid (str): The valid quality status.
        _invalid (str): The invalid quality status.
        _none (str): The none quality status.
    """

    def __init__(self, status: Optional[QualityStatusOptions] = None):
        status = status or QUALITY_STATUS_OPTIONS

        self._valid = status["valid"]
        self._invalid = status["invalid"]
        self._none = status["none"]

    def parse_failure_cases(self, df: pd.DataFrame, number_of_rows: int):
        """
        Parse failure cases from a DataFrame and create corresponding quality issues and status series.

        Args:
            df (pd.DataFrame): The DataFrame containing failure cases.
            number_of_rows (int): The number of rows to generate in the resulting series.

        Returns:
            Tuple[pd.Series, pd.Series]: A tuple containing the quality issues and status series.
        """
        series_issues = self.create_quality_issues_series(df, number_of_rows)
        series_status = self.create_quality_status_series(series_issues)
        return series_issues, series_status

    def create_quality_issues_series(self, df: pd.DataFrame, number_of_rows: int) -> pd.Series:
        """
        Create a quality issues series from a DataFrame of failure cases.

        Args:
            df (pd.DataFrame): The DataFrame containing failure cases.
            number_of_rows (int): The number of rows to generate in the resulting series.

        Returns:
            pd.Series: A quality issues series.
        """
        if df.empty:
            return self.fill_series_with_none(pd.Series(), number_of_rows)

        group_issues = df.groupby("reference")[["column", "check"]]
        series_issues = group_issues.apply(self.create_quality_issues)
        return self.fill_series_with_none(series_issues, number_of_rows)

    def create_quality_issues(self, df: pd.DataFrame) -> str:
        """
        Create a quality issues string from a DataFrame of failure cases.

        Args:
            df (pd.DataFrame): The DataFrame containing failure cases.

        Returns:
            str: A quality issues string.
        """
        cases = [self.create_failure_case(col, ch) for col, ch in zip(df.column, df.check)]

        return " | ".join(cases)

    def create_failure_case(self, column: str, check: str) -> str:
        """
        Create a failure case string for a column and check.

        Args:
            column (str): The name of the column.
            check (str): The description of the check.

        Returns:
            str: A failure case string.
        """
        return f"Column <{column}>: {check}"

    def fill_series_with_none(self, series: pd.Series, number_of_rows: int) -> pd.Series:
        """
        Fill a series with the "none" quality status up to a specified number of rows.

        Args:
            series (pd.Series): The series to fill.
            number_of_rows (int): The number of rows to generate in the resulting series.

        Returns:
            pd.Series: A series filled with the "none" quality status.
        """
        return series.reindex(range(number_of_rows), fill_value=self._none)

    def create_quality_status_series(self, series_issues: pd.Series) -> pd.Series:
        """
        Create a quality status series based on a series of quality issues.

        Args:
            series_issues (pd.Series): A series containing quality issues.

        Returns:
            pd.Series: A series containing quality status based on the issues.
        """
        return pd.Series(np.where(series_issues == self._none, self._valid, self._invalid))
