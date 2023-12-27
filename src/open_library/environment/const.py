#!/usr/bin/env python3

from enum import Enum, auto


class Env(str, Enum):
    DEV = "dev"
    PROD = "prod"
