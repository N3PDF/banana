# -*- coding: utf-8 -*-

from ..data import db, sql


class TableManager:
    """
    Wrapper to a single table

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        DB ORM session
    table_object : sqlalchemy.ext.declarative.api.DeclarativeMeta
        table object
    """

    def __init__(self, session, table_object):
        self.session = session
        self.table_object = table_object

    def truncate(self):
        """Truncate all elements."""
        # deny rest
        if self.table_object != db.Log:
            raise RuntimeError("only logs are allowed to be emptied by this interface!")
        # ask for confirmation
        if input("Purge all logs? [y/n]") != "y":
            print("Doing nothing.")
            return

    def all(self):
        """Retrieve all entries"""
        return sql.select_all(self.session, self.table_object)

    def get(self, hash_partial):
        """Retrieve an entry"""
        return sql.select_hash(self.session, self.table_object, hash_partial)
