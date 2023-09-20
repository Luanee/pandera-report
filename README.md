<h1 align="center">
  Pandera Extension for row-based reporting
</h1>

---

`pandera` provides a flexible and expressive API for performing data
validation on dataframe-like objects to make data processing pipelines more
readable and robust (source: [pandera](https://github.com/unionai-oss/pandera) )

If you have to provide potential quality issues resulting from the dataframe validation via `pandera`, than `pandera-report` is your friend. Based on the validation issues that pandera provides, your original dataframe will be extended with these issues on a row-level base.

With
`pandera-report`, you can:

- Seamlessly integrates with the `pandera` library to provide enhanced data validation capabilities without interfering with the pandera functionality.
- Provides a convenient way to enrich your data with information about why specific rows failed validation.

## Install

Using pip:

```bash
pip install pandera-report
```

## Quick start

The following example is taken from the `pandera` documentation and shows the definition of a DataFrameSchema which will end in a valid result for the provided dataframe.

```python
import pandas as pd
import pandera as pa


# data to validate
df = pd.DataFrame({
    "column1": [1, 4, 0, 10, 9],
    "column2": [-1.3, -1.4, -2.9, -10.1, -20.4],
    "column3": ["value_1", "value_2", "value_3", "value_2", "value_1"]
})

# define schema
schema = pa.DataFrameSchema({
    "column1": pa.Column(int, checks=pa.Check.le(10)),
    "column2": pa.Column(float, checks=pa.Check.lt(-1.2)),
    "column3": pa.Column(str, checks=[
        pa.Check.str_startswith("value_"),
        # define custom checks as functions that take a series as input and
        # outputs a boolean or boolean Series
        pa.Check(lambda s: s.str.split("_", expand=True).shape[1] == 2)
    ]),
})

validated_df = schema(df)
print(validated_df)

#     column1  column2  column3
#  0        1     -1.3  value_1
#  1        4     -1.4  value_2
#  2        0     -2.9  value_3
#  3       10    -10.1  value_2
#  4        9    -20.4  value_1
```

To make usage of the pandera-report functionality for the same schema and dataframe, you can do this:

```python

validator = DataFrameValidator() # default is quality_report=True, lazy=True
print(validator.validate(schema, df))

#     column1  column2  column3 quality_issues quality_status
#  0        1     -1.3  value_1           None          Valid
#  1        4     -1.4  value_2           None          Valid
#  2        0     -2.9  value_3           None          Valid
#  3       10    -10.1  value_2           None          Valid
#  4        9    -20.4  value_1           None          Valid
```

You see?! Same result but extended by the fact that the validation of the dataframe was completely valid. This can also be deactivated for the case that everything is 100% valid.

But what if the dataframe contains data quality issues? `pandera` will throw SchemaErrors or SchemaError (depends on the lazyness). Let's see what `pandera-report` does, if we change the dataframe against the schema definition:

```python

# data to validate
df = pd.DataFrame({
    "column1": [1, 4, 0, 10, 9],
    "column2": [-1.3, -1.4, -2.9, -10.1, -20.4],
    "column3": ["value_1", "value_2", "value_3", "value_2", "value1"]
})

validator = DataFrameValidator()
print(validator.validate(schema, df))

#     column1  column2  column3                              quality_issues quality_status
#  0        1     -1.3  value_1                                        None          Valid
#  1        4     -1.4  value_2                                        None          Valid
#  2        0     -2.9  value_3                                        None          Valid
#  3       10    -10.1  value_2                                        None          Valid
#  4        9    -20.4   value1  Column <column3>: str_startswith('value_')        Invalid
```
