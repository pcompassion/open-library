#!/usr/bin/env python3

from enum import Enum, auto


class Environment(str, Enum):
    DEV = "dev"
    PROD = "prod"
