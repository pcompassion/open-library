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
