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

    def get(self, hash_or_uid):
        """Retrieve an entry

        Parameters
        ----------
        hash_or_uid: str or int
            if :class:`str` partial hash to match (corresponding to the first
            ``len(hash_or_uid)`` characters of the hash), if :class:`int`:

            - if positive: the `uid` of the record to retrieve
            - if negative: position from last
        """
        if isinstance(hash_or_uid, str):
            return sql.select_by_hash(self.session, self.table_object, hash_or_uid)
        elif isinstance(hash_or_uid, int):
            if hash_or_uid >= 0:
                return sql.select_by_uid(self.session, self.table_object, hash_or_uid)
            else:
                return sql.select_by_position(
                    self.session, self.table_object, hash_or_uid
                )
        else:
            raise ValueError(
                "The key passed do not correspond nor to partial hash,"
                " neither to an uid."
            )
