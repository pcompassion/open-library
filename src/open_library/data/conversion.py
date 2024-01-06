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
    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = await as_list_type(value, data_type, field_names)

        return data

    if data_type == ListDataType.Queryset:
        assert isinstance(data, QuerySet[Any]), "data is not QuerySet"
        return data
    elif data_type == ListDataType.ListDict:
        field_names = field_names or []

        if isinstance(data, QuerySet[Any]):
            qs = data
            return await sync_to_async(qs.values)(*field_names)
        elif isinstance(data, pd.DataFrame):
            return data.to_dict(orient="records")
        elif isinstance(data, list):
            if not data or any(isinstance(item, dict) for item in data):
                return data
    elif data_type == ListDataType.Dataframe:
        if isinstance(data, pd.DataFrame):
            return data
        return await read_frame(data, field_names=field_names)
    elif data_type == ListDataType.List:
        if isinstance(data, list):
            return data
        elif isinstance(data, QuerySet[Any]):
            qs = data
            return await sync_to_async(list)(qs)

    raise ValueError("Invalid data type specified.")
