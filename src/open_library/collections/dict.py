#!/usr/bin/env python3
import json


def hashable_json(obj):
    return json.dumps(obj, sort_keys=True)
