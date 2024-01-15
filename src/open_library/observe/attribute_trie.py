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
        # key = data
        # key = data.spec_type_name
        self._insert(data, self.root, key)
        attr_count = data.attr_count()
        self.attr_counts[key] = AttributeCount(data, attr_count)

    def _insert(self, data: AttributeProtocol, node: dict, key: any, remove=False):
        if hasattr(data, "attr_names"):
            for attr_name in data.attr_names():
                attr_value = data.attr_value(attr_name)
                if not attr_value:  # empty value
                    continue

                if attr_name not in node:
                    node[attr_name] = {}

                node_next = node[attr_name]

                self._insert(attr_value, node_next, key)
        else:
            if data not in node:
                node[data] = {}

            node_next = node[data]

            if "@" not in node_next:
                node_next["@"] = set()

            if remove:
                node_next["@"].remove(key)
            else:
                node_next["@"].add(key)

    def remove(self, data: AttributeProtocol):
        key = hash(data)
        # key = data

        self._insert(data, self.root, key, remove=True)
        del self.attr_counts[key]

    def search(self, data: AttributeProtocol) -> list[AttributeProtocol]:
        key = hash(data)
        # key = data
        # key = data.spec_type_name

        found_dict = defaultdict(int)
        search_result = []

        self._search(data, self.root, key, found_dict, search_result)

        return search_result

    def _search(
        self,
        data: AttributeProtocol,
        node: dict,
        key: any,
        found_dict: dict,
        search_result: list[AttributeProtocol],
    ):
        # if data is a AttributeProtocol
        if hasattr(data, "attr_names"):
            for attr_name in data.attr_names():
                if attr_name in node:
                    node_next = node[attr_name]
                else:
                    continue

                attr_value = data.attr_value(attr_name)
                self._search(attr_value, node_next, key, found_dict, search_result)
        else:
            attribute_count = self.attr_counts[key]
            if data not in node:
                return

            node_next = node[data]
            if "@" in node_next:
                for key_ in node_next["@"]:
                    found_dict[key_] += 1

                    if attribute_count.count == found_dict[key_]:
                        found_data = attribute_count.data
                        search_result.append(found_data)
