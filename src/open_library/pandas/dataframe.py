#!/usr/bin/env python3
import pandas as pd

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
