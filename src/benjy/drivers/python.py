import pandas as pd
import os
from functools import singledispatch
from typing import Any, Callable
from ..datatypes import Float, Integer, Timestamp
from visions import StandardSet

typeset = StandardSet()

def identify_source(source):
    ext = os.path.splitext(source)[1]
    return ext


def loader(source):
    source_types = {
        '.csv': pd.read_csv
    }
    source_type = identify_source(source)
    return source_types[source_type]


def writer(destination):
    target_types = {
        '.csv': lambda df, destination: df.to_csv(destination, index=False)
    }
    target_type = identify_source(destination)
    return target_types[target_type]


@singledispatch
def coerce_to_type(datatype: Any) -> Callable:
    return


@coerce_to_type.register
def _(datatype: Timestamp):
    def coerce_frequency(seq):
        seq = pd.to_datetime(seq)
        return seq.dt.floor(datatype.frequency)

    if datatype.frequency is None:
        fn = pd.to_datetime
    else:
        fn = coerce_frequency

    return fn


@coerce_to_type.register
def _(datatype: Integer):
    return lambda x: x.astype(int)


@coerce_to_type.register
def _(datatype: Float):
    return lambda x: x.astype(float)


class PythonDriver:
    @staticmethod
    def load(source, *args, **kwargs):
        source_loader = loader(source)
        return source_loader(source, *args, **kwargs)

    @staticmethod
    def write(data, destination):
        destination_writer = writer(destination)
        destination_writer(data, destination)

    @staticmethod
    def concat(tables):
        return pd.concat(tables, ignore_index=True)

    @staticmethod
    def select(table, columns, columns_as=None):
        columns = [columns] if isinstance(columns, str) else columns
        result = table[columns]

        if columns_as is not None:
            result = result.rename(columns=columns_as)
        return result

    @staticmethod
    def assign_type(table, column, datatype):
        table[column] = coerce_to_type(datatype)(table[column])
        return table

    @staticmethod
    def aggregate(table, group_keys, aggregates):
        return table.groupby(group_keys, as_index=False).agg(aggregates)