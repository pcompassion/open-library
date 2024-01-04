#!/usr/bin/env python3
import json


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
