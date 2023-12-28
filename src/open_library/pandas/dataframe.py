#!/usr/bin/env python3
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


def read_frame(qs: QuerySet, field_names: list = None) -> pd.DataFrame:
    """
    Read a QuerySet into a pandas DataFrame
    :param qs: QuerySet
    :param field_names: list of fields to include in the DataFrame
    :return: DataFrame
    """
    if field_names is None:
        field_names = [f.name for f in qs.model._meta.fields]

    df = pd.DataFrame.from_records(qs.values_list(*field_names), columns=field_names)
    return df
