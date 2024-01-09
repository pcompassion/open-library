#!/usr/bin/env python3

from dataclasses import dataclass
from collections import defaultdict
from open_library.base_spec.base_spec import AttributeProtocol


@dataclass
class AttributeCount:
    data: AttributeProtocol
    count: int


class AttributeTrie:
    def __init__(self):
        self.root = defaultdict(dict)
        self.attr_counts = {}

    def insert(self, data: AttributeProtocol):
        key = hash(data)
        self._insert(data, self.root, key)
        attr_count = data.attr_count()
        self.attr_counts[key] = AttributeCount(data, attr_count)

    def _insert(self, data: AttributeProtocol, node: dict, key: int, remove=False):
        if hasattr(data, "attr_names"):
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

        if remove:
            node["@"].remove(key)
        else:
            node["@"].add(key)

    def remove(self, data: AttributeProtocol):
        key = hash(data)

        self._insert(data, self.root, key, remove=True)
        del self.attr_counts[key]

    def search(self, data: AttributeProtocol) -> list[AttributeProtocol]:
        key = hash(data)

        found_dict = defaultdict(int)
        search_result = []

        self._search(data, self.root, key, found_dict, search_result)

        return search_result

    def _search(
        self,
        data: AttributeProtocol,
        node: dict,
        key: int,
        found_dict: dict,
        search_result: list[AttributeProtocol],
    ):
        # if data is a AttributeProtocol
        if hasattr(data, "attr_names"):
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
