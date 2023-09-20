import warnings
from typing import (
    Callable,
    cast,
    Optional,
    Type,
    TypedDict,
)

import pandas as pd
import pandera as pa
from pandera.errors import SchemaError, SchemaErrors

from pandera_report.options import QUALITY_COLUMNS_OPTIONS, QualityColumnsOptions
from pandera_report.parser import DefaultFailureCaseParser, FailureCaseParser


class DataFrameValidator:
    def __init__(
        self,
        quality_report: bool = True,
        lazy: bool = True,
        columns: Optional[QualityColumnsOptions] = None,
        parser: Optional[FailureCaseParser] = None,
    ):
        self.quality_report = quality_report
        self.lazy = lazy
        self._columns = columns or QUALITY_COLUMNS_OPTIONS

        self._col_issues = self._columns["issues"]
        self._col_status = self._columns["status"]
        self._parser = parser or DefaultFailureCaseParser()

    @property
    def columns(self) -> TypedDict:
        return self._columns

    def validate(self, schema: Type[pa.DataFrameModel] | pa.DataFrameSchema, df: pd.DataFrame) -> pd.DataFrame:
        if not isinstance(schema, pa.DataFrameSchema):
            schema = schema.to_schema()

        error: Optional[SchemaError | SchemaErrors] = None

        try:
            df = schema.validate(df, lazy=self.lazy)
            df_failure = pd.DataFrame()
        except (SchemaErrors, SchemaError) as schema_error:
            df_failure = cast(pd.DataFrame, schema_error.failure_cases)
            error = schema_error

        if not self.quality_report:
            if error:
                raise error
            return df

        if not self.lazy:
            warnings.warn(
                "The DataFrame may have significantly more errors, but based on the lazy setting, only the first error will be marked"
            )

        return self.assign_quality_report(df, df_failure, error if isinstance(error, SchemaError) else None)

    def assign_quality_report(
        self, df: pd.DataFrame, df_failure: pd.DataFrame, error: Optional[SchemaError]
    ) -> pd.DataFrame:
        number_of_rows = df.shape[0]

        if not df_failure.empty:
            df_failure = self.validate_failure_case_dataframe(df_failure, error)
            df_failure = self.transform_failure_cases_dataframe(df_failure, number_of_rows)

        series_issues, series_status = self._parser.parse_failure_cases(df_failure, number_of_rows)

        return df.assign(**{self._col_issues: series_issues, self._col_status: series_status})

    def validate_failure_case_dataframe(self, df_failure: pd.DataFrame, error: Optional[SchemaError]) -> pd.DataFrame:
        df_failure = df_failure.rename(columns={"index": "reference", "failure_case": self._col_issues})

        if error:
            df_failure["column"] = df_failure[self._col_issues]
            df_failure["check"] = error.check

        return df_failure

    def transform_failure_cases_dataframe(self, df_failure: pd.DataFrame, rows: int) -> pd.DataFrame:
        df_failure_columns = self.filter_by_reference(df_failure, pd.isna)
        df_failure_rows = self.filter_by_reference(df_failure, pd.notna)

        df_failure_columns = self.duplicate_column_based_failures(df_failure_columns, rows)

        return pd.concat([df_failure_columns, df_failure_rows])

    def duplicate_column_based_failures(self, df_failure_columns: pd.DataFrame, rows: int) -> pd.DataFrame:
        references = list(range(0, rows)) * df_failure_columns.shape[0]
        df_failure_columns = df_failure_columns.loc[df_failure_columns.index.repeat(rows)]
        df_failure_columns.reference = references
        return df_failure_columns

    def filter_by_reference(self, df: pd.DataFrame, pd_func: Callable[[pd.Series], pd.Series]) -> pd.DataFrame:
        mask = pd_func(df.reference)
        df = df[mask]

        return df.fillna({"column": df[self._col_issues]})
