#!/usr/bin/env python3


class Hashabledict(dict):
    # order dependent.. bah
    def __hash__(self):
        return hash(frozenset(self))
