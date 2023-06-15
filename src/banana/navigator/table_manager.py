from ..data import sql


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
        # ask for confirmation
        if input("Purge all elements? [y/N]").lower() != "y":
            print("Doing nothing.")
        else:
            sql.truncate(self.session, self.table_object)

    def remove(self, records):
        """Remove given elements.

        Parameters
        ----------
        records: list(str or int or dict)
            records to remove, specified as:

            - :class:`str`: partial hash
            - :class:`int`, ``>=0``: uid
            - :class:`int`, ``<0``: position from the end of the table
            - :class:`dict`: the record itself

        """
        uids = []
        for rec in records:
            if isinstance(rec, str):
                record = sql.select_by_hash(self.session, self.table_object, rec)
                uid = record["uid"]
            elif isinstance(rec, int) and rec >= 0:
                uid = rec
            elif isinstance(rec, int) and rec < 0:
                record = sql.select_by_position(self.session, self.table_object, rec)
                uid = record["uid"]
            elif isinstance(rec, dict):
                uid = rec["uid"]
            else:
                raise ValueError(
                    f"The element {rec} can not be used to identify a record"
                )
            uids.append(uid)

        sql.remove(self.session, self.table_object, uids)

    def update_atime(self, records):
        """Update access time for given records.

        Parameters
        ----------
        records: list(dict)
            records to update

        """
        sql.update_atime(
            self.session, self.table_object, [rec["uid"] for rec in records]
        )

    def all(self):
        """Retrieve all entries

        Returns
        -------
        list(dict)
            the retrieved entries

        """
        records = sql.select_all(self.session, self.table_object)
        self.update_atime(records)

        return records

    def get(self, hash_or_uid):
        """Retrieve an entry

        Parameters
        ----------
        hash_or_uid: str or int
            if :class:`str` partial hash to match (corresponding to the first
            ``len(hash_or_uid)`` characters of the hash), if :class:`int`:

            - if positive: the `uid` of the record to retrieve
            - if negative: position from last

        Returns
        -------
        dict
            the retrieved entry

        Raises
        ------
        sql.RetrieveError
            if not a single entry corresponds to the give identifier (so both
            for no entries and multiple entries)

        """
        if isinstance(hash_or_uid, str):
            record = sql.select_by_hash(self.session, self.table_object, hash_or_uid)
        elif isinstance(hash_or_uid, int):
            if hash_or_uid >= 0:
                record = sql.select_by_uid(self.session, self.table_object, hash_or_uid)
            else:
                record = sql.select_by_position(
                    self.session, self.table_object, hash_or_uid
                )
        else:
            raise ValueError(
                "The key passed do not correspond nor to partial hash,"
                " neither to an uid."
            )

        self.update_atime([record])
        return record
