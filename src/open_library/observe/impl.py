#!/usr/bin/env python3
from pydantic import BaseModel
import operator
import functools

from dataclasses import dataclass
from collections import defaultdict
from typing import Protocol


class AttributeProtocol(Protocol):
    def attr_names(self) -> list[str]:
        ...

    def attr_value(self, attr_name: str) -> AttributeProtocol:
        ...

    def __hash__(self) -> int:
        ...

    def attr_count(self) -> int:
        ...

class EventSpec(BaseModel):

    spec_name: str

    def attr_names(self):
        attr_names = self.model_dump().keys()

        return attr_names

    def attr_value(self, attr_name: str) -> AttrsProtocol:
        attr_value = getattr(self, attr_name)

        return attr_value

    def attr_count(self) -> int:

        return len(self.attr_names())

class QuoteEventSpec(EventSpec):
    spec_type_name: str = "quote",
    security_code: str | None,
    security_type: SecurityType | list[SecurityType] | None

    def __hash__(self) -> int:

        hash_keys = ["spec_type_name", "security_code", "security_type"]

        attrs_hash = map(hash, hash_keys)

        return functools.reduce(operator.xor, attrs_hash, 0)

@dataclass
class AttributeCount:
    data: AttrsProtocol
    count: int

class AttributeTrie:
    def __init__(self):
        self.root = defaultdict(dict)
        self.attr_counts = {}

    def insert(self, data: AttrsProtocol):
        key = hash(data)
        self._insert(data, self.root, key)
        attr_count = data.attr_count()
        self.attr_counts[key] = AttributeCount(data, attr_count)

    def _insert(self, data: AttrsProtocol, node: dict, key: int):
        for attr_name in data.attr_names():
            if attr_name in node:
                node = node[attr_name]
            else:
                node[attr_name] = defaultdict(dict)
                node = node[attr_name]

            attr_value = data.attr_value(attr_name)
            self._insert(attr_value, node, key)

        if "@" not in node:
            node["@"] = set()
        node["@"].add(key)

    def search(self, data: AttrsProtocol) -> list[AttrsProtocol]:
        key = hash(data)

        found_dict = defaultdict(int)
        search_result = []

        self._search(data, self.root, key, found_dict, search_result)

        return search_result

    def _search(
            self, data: AttrsProtocol, node: dict, key: int, found_dict: dict, search_result: list[AttrsProtocol]
    )
        for attr_name in data.attr_names():
            if attr_name in node:
                node = node[attr_name]
            else:
                return

            attr_value = data.attr_value(attr_name)
            self._search(attr_value, node, key, found_dict, search_result)

        if "@" in node:
            for key in node["@"]:
                found_dict[key] += 1
                attribute_count = self.attr_counts[key]
                if attribute_count.count == found_dict[key]:

                    found_data = attribute_count.data
                    search_result.append(found_data)
