# -*- coding: utf-8 -*-

from ..data import sql


class TableManager:
    """
    Wrapper to a single table

    Parameters
    ----------
        conn : sqlite3.Connection
            DB connection
        table_name : str
            table name
    """

    def __init__(self, conn, table_name):
        self.conn = conn
        self.table_name = table_name

    def truncate(self):
        """Truncate all elements."""
        # deny rest
        if self.table_name != "logs":
            raise RuntimeError("only logs are allowed to be emptied by this interface!")
        # ask for confirmation
        if input("Purge all logs? [y/n]") != "y":
            print("Doing nothing.")
            return

    def all(self):
        """Retrieve all entries"""
        return sql.select_all(self.conn, self.table_name)

    def get(self, hash_partial):
        """Retrieve an entry"""
        return sql.select_hash(self.conn, self.table_name, bytes.fromhex(hash_partial))
