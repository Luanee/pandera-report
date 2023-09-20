from contextlib import nullcontext as do_not_raise
from typing import (
    Any,
    Optional,
    Type,
)

import pandas as pd
import pandera as pa
import pytest
from pandera.errors import SchemaError, SchemaErrors
from pandera.typing import Series

from pandera_report.options import QualityColumnsOptions
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

    @pa.check("column3", name="column3")
    def custom_check(cls, value: Series[str]):
        return value.str.split("_", expand=True).shape[1] == 2


data = {
    "column1": [9, 4, 0, 10, 1],
    "column2": [-1.3, -4, -8, -10, -3],
    "column3": ["value_1", "value_2", "value_3", "value_2", "value_1"],
}

invalid_data = {
    "column1": [9, 4, 0, 10, 1],
    "column3": ["value_1", "value_2", "value_3", "value_2", "value1"],
}

custom_columns: QualityColumnsOptions = {"issues": "what's that?", "status": "does it work?"}


@pytest.mark.parametrize(
    "data,schema,quality_report,lazy,columns,parser,exception",
    [
        (data, schema, False, False, None, None, do_not_raise()),
        (data, schema, False, True, None, None, do_not_raise()),
        (data, schema, True, False, None, None, do_not_raise()),
        (data, schema, True, True, None, None, do_not_raise()),
        (data, schema, True, True, custom_columns, None, do_not_raise()),
        (data, SchemaModel, True, True, custom_columns, None, do_not_raise()),
        (invalid_data, schema, False, False, None, None, pytest.raises(SchemaError)),
        (invalid_data, schema, False, True, None, None, pytest.raises(SchemaErrors)),
        (invalid_data, schema, True, False, None, None, do_not_raise()),
        (invalid_data, schema, True, True, None, None, do_not_raise()),
    ],
)
def test_validator_validate(
    data: dict,
    schema: Type[pa.DataFrameModel] | pa.DataFrameSchema,
    quality_report: bool,
    lazy: bool,
    columns: Optional[QualityColumnsOptions],
    parser: Optional[FailureCaseParser],
    exception,
):
    df = pd.DataFrame(data)
    org_columns = df.columns.to_list()
    validator = DataFrameValidator(quality_report, lazy, columns, parser)

    with exception:
        df = validator.validate(schema, df)

        if quality_report:
            assert df.columns.to_list() == org_columns + list(validator.columns.values())
