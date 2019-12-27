# e2fyi-pyspark

[![PyPI version](https://badge.fury.io/py/e2fyi-pyspark.svg)](https://badge.fury.io/py/e2fyi-pyspark)
[![Build Status](https://travis-ci.org/e2fyi/pyspark-utils.svg?branch=master)](https://travis-ci.org/e2fyi/pyspark-utils)
[![Coverage Status](https://coveralls.io/repos/github/e2fyi/pyspark-utils/badge.svg?branch=master)](https://coveralls.io/github/e2fyi/pyspark-utils?branch=master)
[![Documentation Status](https://readthedocs.org/projects/e2fyi-pyspark/badge/?version=latest)](https://e2fyi-pyspark.readthedocs.io/en/latest/?badge=latest)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Downloads](https://pepy.tech/badge/e2fyi-pyspark)](https://pepy.tech/project/e2fyi-pyspark)

`e2fyi-pyspark` is an `e2fyi` namespaced python package with `pyspark` subpackage
(i.e. `e2fyi.pyspark`) which holds a collections of useful functions for common
but painful pyspark tasks.

API documentation can be found at [https://e2fyi-pyspark.readthedocs.io/en/latest/](https://e2fyi-pyspark.readthedocs.io/en/latest/).

Change logs are available in [CHANGELOG.md](./CHANGELOG.md).

> - Python 3.6 and above
> - Licensed under [Apache-2.0](./LICENSE).

## Quickstart

```bash
pip install e2fyi-pyspark
```

### Infer schema for unknown json strings inside a pyspark dataframe

`e2fyi.pyspark.schema.infer_schema_from_rows` is a util function to infer the
schema of unknown json strings inside a pyspark dataframe - i.e. so that the
schema can be subsequently used to parse the json string into a typed data
structure in the dataframe
(see [`pyspark.sql.functions.from_json`](https://spark.apache.org/docs/latest/api/python/pyspark.sql.html#pyspark.sql.functions.from_json)).

```py
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
# should have a column "data" with a proper schema
df.printSchema()
```
