from contextlib import nullcontext as do_not_raise
from typing import (
    cast,
    Optional,
    Type,
    Union,
)

import pandas as pd
import pandera as pa
import pytest
from pandera.errors import SchemaError, SchemaErrors
from pandera.typing import Series

from pandera_report.options import QUALITY_COLUMNS_OPTIONS, QualityColumnsOptions
from pandera_report.parser import FailureCaseParser
from pandera_report.validator import DataFrameValidator

schema = pa.DataFrameSchema(
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


class SchemaModel(pa.DataFrameModel):
    column1: Series[int] = pa.Field(le=10)
    column2: Series[float] = pa.Field(lt=-1.2)
    column3: Series[str] = pa.Field(str_startswith="value_")

    @pa.dataframe_check
    def contains_data(cls, df: pd.DataFrame) -> bool:
        return df.size > 0

    @pa.check("column3", name="column3")
    def custom_check(cls, value: Series[str]) -> bool:
        return value.str.split("_", expand=True).shape[1] == 2


class EmptySchemaModel(pa.DataFrameModel):
    column1: Series[int] = pa.Field(nullable=True, coerce=True)
    column2: Series[float] = pa.Field(nullable=True)
    column3: Series[str] = pa.Field(nullable=True)


custom_columns: QualityColumnsOptions = {"issues": "what's that?", "status": "does it work?"}


@pytest.mark.parametrize(
    "df_fixture,schema,quality_report,lazy,columns,parser,exception",
    [
        ("df_valid", schema, False, False, None, None, do_not_raise()),
        ("df_valid", schema, False, True, None, None, do_not_raise()),
        ("df_valid", schema, True, False, None, None, do_not_raise()),
        ("df_valid", schema, True, True, None, None, do_not_raise()),
        ("df_valid", schema, True, True, custom_columns, None, do_not_raise()),
        ("df_valid", SchemaModel, True, True, custom_columns, None, do_not_raise()),
        ("df_invalid_values", schema, False, False, None, None, pytest.raises(SchemaError)),
        ("df_invalid_values", schema, False, True, None, None, pytest.raises(SchemaErrors)),
        ("df_invalid_values", schema, True, False, None, None, do_not_raise()),
        ("df_invalid_values", schema, True, True, None, None, do_not_raise()),
        ("df_empty", schema, True, True, None, None, do_not_raise()),
        ("df_empty", SchemaModel, True, True, None, None, do_not_raise()),
        ("df_empty", SchemaModel, False, True, None, None, pytest.raises(SchemaErrors)),
    ],
)
def test_validator_validate(
    df_fixture: str,
    schema: Union[Type[pa.DataFrameModel], pa.DataFrameSchema],
    quality_report: bool,
    lazy: bool,
    columns: Optional[QualityColumnsOptions],
    parser: Optional[FailureCaseParser],
    exception,
    request,
):
    df = cast(pd.DataFrame, request.getfixturevalue(df_fixture))
    org_columns = df.columns.to_list()
    validator = DataFrameValidator(quality_report, lazy, columns, parser)

    with exception:
        df = validator.validate(schema, df)

        if quality_report:
            org_columns += list(validator.columns.values())

        assert df.columns.to_list() == org_columns


@pytest.mark.parametrize(
    "df_fixture,schema,validity,expected",
    [
        ("df_valid", schema, True, tuple),
        ("df_valid", schema, False, pd.DataFrame),
    ],
)
def test_validator_validate_flag(
    df_fixture: str,
    schema: Union[Type[pa.DataFrameModel], pa.DataFrameSchema],
    validity: bool,
    expected: Type,
    request,
):
    df = cast(pd.DataFrame, request.getfixturevalue(df_fixture))
    validator = DataFrameValidator()

    df_validated = validator.validate(schema, df, validity_flag=validity)
    assert isinstance(df_validated, expected)


@pytest.mark.parametrize(
    "columns,expected",
    [
        (None, QUALITY_COLUMNS_OPTIONS),
        (custom_columns, custom_columns),
    ],
)
def test_validator_columns(columns: Optional[QualityColumnsOptions], expected: QualityColumnsOptions):
    validator = DataFrameValidator(columns=columns)

    assert validator.columns == expected
