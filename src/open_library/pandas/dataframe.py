#!/usr/bin/env python3
from asgiref.sync import sync_to_async
from typing import Any
import pandas as pd

from django.db.models.query import QuerySet


def serialize_row(row):
    serialized_row = {}
    for key, value in row._asdict().items():
        if isinstance(value, pd.Timestamp):
            serialized_row[
                key
            ] = value.isoformat()  # or use value.timestamp() for Unix timestamp
        else:
            serialized_row[key] = value
    return serialized_row


async def read_frame(
    data: QuerySet[Any] | list[dict], field_names: list | None = None
) -> pd.DataFrame:
    """
    Read a QuerySet into a pandas DataFrame
    :param qs: QuerySet
    :param field_names: list of fields to include in the DataFrame
    :return: DataFrame
    """
    records = []
    if isinstance(data, QuerySet[Any]):
        qs = data
        if field_names is None:
            field_names = [f.name for f in qs.model._meta.fields]

        async_values_list = sync_to_async(lambda: list(qs.values_list(*field_names)))
        records = await async_values_list()
    elif isinstance(data, list):
        records = data

    df = pd.DataFrame.from_records(records, columns=field_names)
    return df
