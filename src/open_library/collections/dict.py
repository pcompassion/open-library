#!/usr/bin/env python3
import json
from uuid import UUID
from datetime import datetime


def hashable_json(obj):
    return json.dumps(obj, sort_keys=True)


def instance_to_dict(instance, fields):
    """
    # Usage
    selected_fields = instance_to_dict(instance, ['field1', 'field2'])
    print(selected_fields)
    """
    return {field: getattr(instance, field) for field in fields}


def rename_keys(original_dict, key_mapping):
    """
    # Example usage:
    original_dict = {'a': 1, 'b': 2, 'c': 3}
    key_mapping = {'a': 'alpha', 'b': None}  # Renames 'a' to 'alpha', keeps 'b' as is, and omits 'c'
    new_dict = transform_dictionary(original_dict, key_mapping)

    print(new_dict)  # Output will be: {'alpha': 1, 'b': 2}
    """
    new_dict = {}
    for old_key, new_key in key_mapping.items():
        if old_key in original_dict:
            # Use the new key name if provided, else use the original key
            new_dict[new_key if new_key else old_key] = original_dict[old_key]
    return new_dict


def filter_dict(original_dict, keys_to_include):
    return {key: original_dict[key] for key in keys_to_include if key in original_dict}


def serialize(dictionary):
    # from pydantic.json_schema import to_jsonable_python
    from pydantic_core import to_json

    return to_json(dictionary)


def to_jsonable_python(dictionary, excludes=None):
    # from pydantic.json_schema import to_jsonable_python
    from pydantic_core import to_jsonable_python

    return to_jsonable_python(dictionary, exclude=excludes)


def deserialize(json_str):
    from pydantic_core import from_json

    return from_json(json_str)


# class CustomEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, UUID):
#             return str(obj)
#         elif isinstance(obj, datetime):
#             return obj.isoformat()
#         return super().default(obj)


# def serialize(data):
#     return json.dumps(data, cls=CustomEncoder)


# def deserialize(json_string):
#     def convert(obj):
#         for key, value in obj.items():
#             try:
#                 obj[key] = UUID(value)
#             except (ValueError, TypeError):
#                 pass
#             try:
#                 obj[key] = datetime.fromisoformat(value)
#             except (ValueError, TypeError):
#                 pass
#         return obj

#     return json.loads(json_string, object_hook=convert)
