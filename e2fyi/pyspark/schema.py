"""
Functions to sample and infer the schema for a json string object inside a
pyspark dataframe.
"""
import json

from typing import Any, List, Union

import pyspark

from pyspark.sql.types import (
    ArrayType,
    FloatType,
    DoubleType,
    StringType,
    StructType,
    BooleanType,
    IntegerType,
    StructField,
)


def infer_type(  # noqa C901 pylint: disable=too-many-return-statements
    value: Any, float_as_double: bool = False
) -> Union[
    ArrayType, FloatType, DoubleType, StringType, StructType, BooleanType, IntegerType
]:
    """
    infer_type returns the pyspark schema representation of any valid python
    object (i.e. string, int, float, dict, list).

    Example::

        from e2fyi.pyspark.schema import infer_type

        print(infer_type(1.0))  # FloatType
        print(infer_type(1.0, float_as_double=True))  # DoubleType

        # StructType(List(StructField(hello,StringType,true)))
        print(infer_type({"hello": "world"}))

        # ArrayType(StructType(List(StructField(hello,StringType,true))),true)
        print(infer_type([{"hello": "world"}]))

    Args:
        value (Any): any valid python object (i.e. string, int, float, dict, list).
        float_as_double (bool, optional): if true, will return all floats as DoubleType.

    Raises:
        ValueError: "Unable to infer type for empty array."
        ValueError: "Unknown value type: Unable to infer pyspark types."

    Returns:
        Union[ArrayType, BooleanType, DoubleType, FloatType, IntegerType, StringType,
        StructType]: pyspark schema
    """
    if isinstance(value, str):
        try:
            return infer_type(json.loads(value))
        except json.JSONDecodeError:
            return StringType()
    if isinstance(value, bool):
        return BooleanType()
    if isinstance(value, int):
        return IntegerType()
    if isinstance(value, float):
        if float_as_double:
            return DoubleType()
        return FloatType()
    if isinstance(value, list):
        if not value:
            raise ValueError("Unable to infer type for empty array.")
        if isinstance(value[0], dict):
            sample = {}
            for item in value:
                sample.update(
                    {key: key_value for key, key_value in item.items() if key_value}
                )
            return ArrayType(infer_type(sample))
        return ArrayType(infer_type(value[0]))
    if isinstance(value, dict):
        fields = [
            StructField(key, infer_type(key_value)) for key, key_value in value.items()
        ]
        return StructType(fields)
    raise ValueError("Unknown value type: Unable to infer pyspark types.")


def infer_schema_from_rows(
    rows: List[pyspark.sql.Row], col: str
) -> Union[
    ArrayType, FloatType, DoubleType, StringType, StructType, BooleanType, IntegerType
]:
    """
    infer_schema_from_rows will attempt infer the schema of the json strings
    in the specified column.

    In order to best estimate the full schema of partial dicts, dicts found
    inside the loaded json string will be merged, while list will be concat
    (and the dict inside merged).

    This inferrence is done on the entire list of pyspark row in local env
    (instead of spark) - i.e. provide a sample of rows instead of the entire
    data set.

    Example::

        import pyspark
        from e2fyi.pyspark.schema import infer_schema_from_rows

        # get spark session
        spark = pyspark.sql.SparkSession.builder.getOrCreate()
        # load a parquet (assume the parquet has a column "json_str", which
        # contains a json str with unknown schema)
        df = spark.read.parquet("s3://some-bucket/some-file.parquet")
        # get 10% of the rows as sample (w/o replacement)
        sample_rows = df.select("json_str").sample(False, 0.01).collect()
        # infer the schema for json str in col "json_str" based on the sample rows
        # NOTE: this is run locally (not in spark)
        schema = infer_schema_from_rows(sample_rows, col="json_str")
        # add a new column "data" which is the parsed json string with a inferred schema
        df = df.withColumn("data", pyspark.sql.functions.from_json("json_str", schema))

    Args:
        rows (List[pyspark.sql.Row]): list of pyspark rows.
        col (str): name of the column with the json string.

    Returns:
        Union[ArrayType,FloatType,DoubleType,StringType,StructType,BooleanType,
        IntegerType]: schema for the json string
    """
    sample_dict = {}
    sample_list: list = []
    sample = None
    for row in rows:
        item = getattr(row, col)
        if isinstance(item, str):
            item = json.loads(item)
        if isinstance(item, dict):
            sample_dict.update({key: value for key, value in item.items() if value})
        if isinstance(item, list):
            sample_list = sample_list + item
        sample = sample or item
    if sample_list:
        return infer_type(sample_list)
    return infer_type(sample_dict) if sample_dict else infer_type(sample)
