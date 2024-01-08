#!/usr/bin/env python3
from enum import Enum


class ListenerType(str, Enum):
    Callable = "callable"
    ChannelGroup = "channel_group"
    Service = "service"
