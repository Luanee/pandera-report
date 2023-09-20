import abc
from typing import Protocol

import numpy as np
import pandas as pd

from .options import QUALITY_STATUS_OPTIONS, QualityStatusOptions


class FailureCaseParser(Protocol):
    @abc.abstractmethod
    def parse_failure_cases(self, df: pd.DataFrame, number_of_rows: int) -> tuple[pd.Series, pd.Series]:
        ...

    @abc.abstractmethod
    def create_quality_issues_series(df: pd.DataFrame) -> pd.Series:
        ...

    @abc.abstractmethod
    def create_quality_status_series(self, df: pd.DataFrame) -> pd.Series:
        ...

    @abc.abstractmethod
    def create_failure_case(self, column: str, check: str) -> str:
        ...


class DefaultFailureCaseParser(FailureCaseParser):
    def __init__(self, status: QualityStatusOptions = QUALITY_STATUS_OPTIONS):
        self._valid = status["valid"]
        self._invalid = status["invalid"]
        self._none = status["none"]

    def parse_failure_cases(self, df: pd.DataFrame, number_of_rows: int):
        series_issues = self.create_quality_issues_series(df, number_of_rows)
        series_status = self.create_quality_status_series(series_issues)
        return series_issues, series_status

    def create_quality_issues_series(self, df: pd.DataFrame, number_of_rows: int) -> pd.Series:
        if df.empty:
            return self.fill_series_with_none(pd.Series(), number_of_rows)

        group_issues = df.groupby("reference")[["column", "check"]]
        series_issues = group_issues.apply(self.create_quality_issues)
        return self.fill_series_with_none(series_issues, number_of_rows)

    def create_quality_issues(self, df: pd.DataFrame) -> str:
        cases = [self.create_failure_case(col, ch) for col, ch in zip(df.column, df.check)]

        return " | ".join(cases)

    def create_failure_case(self, column: str, check: str) -> str:
        return f"Column <{column}>: {check}"

    def fill_series_with_none(self, series: pd.Series, number_of_rows: int) -> pd.Series:
        return series.reindex(range(number_of_rows), fill_value=self._none)

    def create_quality_status_series(self, series_issues: pd.Series) -> pd.Series:
        return pd.Series(np.where(series_issues == self._none, self._valid, self._invalid))
