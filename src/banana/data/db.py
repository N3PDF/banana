# -*- coding: utf-8 -*-

import abc

from . import sql


class TableObject:
    def __init__(self, add_hash=True, prototype=None):
        if prototype is None:
            prototype = {}

        self.fields = {"uid": "INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE"}
        # add explicit hash?
        if add_hash:
            self.fields["hash"] = "BLOB UNIQUE"

        # collect fields
        for k, v in prototype.items():
            self.fields[k] = sql.mapping[type(v)]

    @property
    def sqlfields(self):
        return [f"{k} {v}" for k, v in self.fields.items()]


class Theory(TableObject):
    name = "theory"
    pass


class OCard(abc.ABC):
    pass


class Cache:
    pass


class Log:
    pass
