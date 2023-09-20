import pandas as pd
import pandera as pa

from pandera_report.validator import DataFrameValidator

# data to validate
df = pd.DataFrame(
    {
        "column1": [9, 4, 0, 10, 1],
        "column3": ["value_1", "value_2", "value_3", "value_2", "value1"],
    }
)

# define schema
schema = pa.DataFrameSchema(
    {
        "column1": pa.Column(int, checks=pa.Check.le(10)),
        "column2": pa.Column(float, checks=pa.Check.lt(-1.2)),
        "column3": pa.Column(
            str,
            checks=[
                pa.Check.str_startswith("value_"),
                # define custom checks as functions that take a series as input and
                # outputs a boolean or boolean Series
                pa.Check(lambda s: s.str.split("_", expand=True).shape[1] == 2),
            ],
        ),
    }
)

validator = DataFrameValidator(False, True)
print(validator.validate(schema, df))
