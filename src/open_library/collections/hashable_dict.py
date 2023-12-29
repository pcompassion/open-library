#!/usr/bin/env python3


class Hashabledict(dict):
    # order dependent..
    def __hash__(self):
        return hash(frozenset(self))


class Hashabledict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))
