#!/usr/bin/env python3

from enum import Enum
import pandas as pd
from asgiref.sync import sync_to_async

from typing import Any
from open_library.pandas.dataframe import read_frame
from django.db.models.query import QuerySet


class ListDataType(str, Enum):
    Dataframe = "dataframe"
    Queryset = "queryset"
    List = "list"
    ListDict = "list_dict"


_ListDataTypeHint = list[Any] | pd.DataFrame

ListDataTypeHint = QuerySet[Any] | _ListDataTypeHint | dict[str, _ListDataTypeHint]


async def as_list_type(
    data: ListDataTypeHint,
    data_type: ListDataType,
    field_names: list | None = None,
):
    field_names = field_names or []

    field_names_updated = field_names[:]
    additional_fields = {}

    if isinstance(data, QuerySet) and hasattr(data.model, "_non_database_fields"):
        if field_names:
            for field_name, field in data.model._non_database_fields.items():
                if field_name in field_names_updated:
                    field_names_updated.remove(field_name)
                    dependent_field_names = field.dependent_field_names
                    field_names_updated += dependent_field_names
                    additional_fields[field_name] = field
        else:
            for field_name, field in data.model._non_database_fields.items():
                dependent_field_names = field.dependent_field_names
                field_names_updated += dependent_field_names
                additional_fields[field_name] = field

    additional_field_names = list(additional_fields.keys())

    def add_non_database_fields(row, fields):
        result = []

        for field_name, field in fields.items():
            result.append(field.get(row))
        return result

    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = await as_list_type(value, data_type, field_names)

        return data

    if data_type == ListDataType.Queryset:
        assert isinstance(data, QuerySet[Any]), "data is not QuerySet"
        return data
    elif data_type == ListDataType.ListDict:
        if isinstance(data, QuerySet[Any]):
            qs = data
            df = await read_frame(data, field_names=field_names)
            if additional_field_names and not df.empty:
                df[additional_field_names] = df.apply(
                    lambda x: add_non_database_fields(x, additional_fields), axis=1
                )
            return df.to_dict(orient="records")

        elif isinstance(data, pd.DataFrame):
            return data.to_dict(orient="records")
        elif isinstance(data, list):
            if not data or any(isinstance(item, dict) for item in data):
                return data
    elif data_type == ListDataType.Dataframe:
        if isinstance(data, pd.DataFrame):
            return data
        df = await read_frame(data, field_names=field_names)
        if additional_field_names and not df.empty:
            df[additional_field_names] = df.apply(
                lambda x: pd.Series(add_non_database_fields(x, additional_fields)),
                axis=1,
            )
        return df

    elif data_type == ListDataType.List:
        if isinstance(data, list):
            return data
        elif isinstance(data, QuerySet[Any]):
            qs = data
            return await sync_to_async(list)(qs)

    raise ValueError("Invalid data type specified.")
