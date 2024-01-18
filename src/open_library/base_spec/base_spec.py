#!/usr/bin/env python3
import operator
import functools
from typing import Protocol
from pydantic import BaseModel
from typing import ClassVar


class AttributeProtocol(Protocol):
    def attr_names(self) -> list[str]:
        ...

    def attr_value(self, attr_name: str) -> "AttributeProtocol":
        ...

    def __hash__(self) -> int:
        ...

    def attr_count(self) -> int:
        ...

    def from_dict(cls, data: dict) -> "AttributeProtocol":
        ...


class BaseSpec(BaseModel):
    spec_type_name_classvar: ClassVar[str]
    spec_type_name: str = ""

    def attr_names(self) -> list[str]:
        names = self.model_dump(
            exclude_none=True, exclude=set(["data", "service_keys"])
        ).keys()
        names = list(names)
        return names

    def attr_value(self, attr_name: str) -> AttributeProtocol:
        value = getattr(self, attr_name)

        return value

    def attr_count(self) -> int:
        return len(self.attr_names())

    def __hash__(self) -> int:
        hash_keys = self.hash_keys or []
        values_to_hash = (getattr(self, key) for key in hash_keys)

        attrs_hash = map(hash, values_to_hash)

        return functools.reduce(operator.xor, attrs_hash, 0)

    @classmethod
    def from_dict(cls, data: dict):
        # Convert the params field to an AttributeProtocol-conforming object

        for key, value in data.items():
            if isinstance(value, dict):
                param_cls: AttributeProtocol = cls.model_fields[key].annotation
                data[key] = param_cls.from_dict(value)

        # Create an instance of ListenerSpec with the processed data
        return cls(**data)

    @property
    def hash_keys(self):
        pass
