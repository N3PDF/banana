# -*- coding: utf-8 -*-
import pickle
import hashlib
import copy
import sqlite3

from banana.data import dfdict

mapping = {
    int: "INTEGER",
    float: "REAL",
    str: "TEXT",
    dict: "BLOB",
    list: "BLOB",
    bytes: "BLOB",
    bool: "BOOL",
    dfdict.DFdict: "BLOB",
}
"""
Mapping of Python types to SQLite types.
"""


def create_table(name, obj, add_hash=True):
    """
    SQL command for creating the table

    Parameters
    ----------
        name : str
            table name
        obj : dict
            column-names to example values mapping
        add_hash : bool
            add hash field?

    Returns
    -------
        tmpl : str
            SQL command
    """
    tmpl = f"CREATE TABLE {name} (\n"
    fields = ["uid INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE"]
    # add explicit hash?
    if add_hash:
        fields.append("hash BLOB UNIQUE")
    # collect fields
    for k, v in obj.items():
        fields.append(f"{k} {mapping[type(v)]}")
    # collect
    tmpl += ",\n".join(fields)
    tmpl += "\n);"
    return tmpl


def serialize(data):
    """
    Eventually turn some elements into their binary representation.

    Parameters
    ----------
        data : dict
            raw data

    Returns
    -------
        ndata : list
            improved data
    """
    blobbed_types = [list, dict, dfdict.DFdict]
    sorted_data = dict(sorted(data.items()))
    ndata = []
    for d in sorted_data.values():
        if type(d) in blobbed_types:
            ndata.append(pickle.dumps(d))
        else:
            ndata.append(d)
    return tuple(ndata)


def deserialize(data, fields):
    """
    Undo the binary representation.

    Parameters
    ----------
        data : list
            raw data
        fields : list(str)
            fields

    Returns
    -------
        obj : dict
            composed object
    """
    obj = {}
    for f, el in zip(fields, data):
        if isinstance(el, bytes) and "hash" not in f:
            obj[f] = pickle.loads(el)
        else:
            obj[f] = el
    return obj


def fields(conn, table):
    """
    Retrieve the list of fields for this table (from SQL)

    Parameters
    ----------
        conn : sqlite3.Connection
            database
        table : string
            target table

    Returns
    -------
        list(str)
            fields
    """
    with conn:
        fs = conn.execute("pragma table_info(%s)" % table).fetchall()
    return [f[1] for f in fs]


def add_hash(record):
    """
    Add a hash value as last element to the record.

    Parameters
    ----------
        record : tuple
            data

    Returns
    -------
        hashed_record : tuple
            data + hash
    """
    h = hashlib.sha256(pickle.dumps(record))
    return (*record, h.digest())


class RecordsFrame:
    """
    Container to communicate with the database.

    Parameters
    ----------
        fields : list
            list with all fields
        records : list
            list with all records
    """

    def __init__(self, fields, records):
        self.fields = fields
        self.records = records


def prepare_records(base, updates):
    """
    Generate all records from the base.

    Parameters
    ----------
        base : dict
            base record
        updates : dict
            update directives

    Returns
    -------
        documents : list(dict)
            list of all dictionaries
        rf : RecordsFrame
            all records ready for insertion
    """
    records = []
    documents = []
    for upd in updates:
        document = copy.deepcopy(base)
        document.update(upd)
        documents.append(document)
        # add the hash when there is NO meta data around
        serialized_record = serialize(document)
        hashed_record = add_hash(serialized_record)
        document["hash"] = hashed_record[-1]
        records.append(hashed_record)
    return (documents, RecordsFrame(list(base.keys()) + ["hash"], records))


def question_args(seq):
    """
    Join sufficient ?s (Not only 3)

    See: https://de.wikipedia.org/wiki/Die_drei_%3F%3F%3F

    Parameters
    ----------
        seq : list
            arguments

    Returns
    -------
        str
            sql template
    """
    return "(" + ",".join(list("?" * len(seq))) + ")"


def insertmany(conn, table, rf):
    """
    Insert all records into the DB.

    Parameters
    ----------
        conn : sqlite3.Connection
            database
        table : string
            target table
        rf : RecordsFrame
            list with all records
    """
    tmpl = (
        f"INSERT INTO {table}("
        + ",".join(rf.fields)
        + f") VALUES {question_args(rf.fields)}"
    )
    with conn:
        conn.executemany(tmpl, rf.records)


def insertnew(conn, table, rf):
    """
    Insert all records that do not exist yet (determined by hash).


    Parameters
    ----------
        conn : sqlite3.Connection
            database
        table : string
            target table
        rf : RecordsFrame
            list with all records
    """
    # check if they already exist
    hash_idx = rf.fields.index("hash")
    with conn:
        elems = conn.execute(
            f"SELECT hash FROM {table} WHERE hash IN {question_args(rf.records)}",
            [r[hash_idx] for r in rf.records],
        )
        available = list(map(lambda x: x[0], elems.fetchall()))
        new_records = list(filter(lambda x: x[hash_idx] not in available, rf.records))
    # insert them now
    insertmany(conn, table, RecordsFrame(rf.fields, new_records))


class HashError(KeyError):
    def __init__(self, descr, hashes=None):
        if hashes is not None:
            msg = "the following hashes have been found:"
            msg += "\n- " + "\n- ".join(hashes) + "\n"
        super().__init__(descr)


def select_hash(conn, table, bin_hash_partial):
    """
    Find a record by its hash.

    Parameters
    ----------
        conn : sqlite3.Connection
            database
        table : string
            target table
        bin_hash_partial : bytes
            binary hash identifier

    Returns
    -------
        dict
            record
    """
    with conn:
        elems = conn.execute(
            f"SELECT * FROM {table} WHERE SUBSTR(hash,1,{len(bin_hash_partial)}) = ?",
            [sqlite3.Binary(bin_hash_partial)],
        )
        available = elems.fetchall()
    # too much?
    if len(available) > 1:
        raise HashError("hash is not unique", available)
    elif len(available) < 1:
        raise HashError("hash not found")
    # deserialize the thing
    fs = fields(conn, table)
    return deserialize(available[0], fs)


def select_all(conn, table):
    """
    Collect all records.

    Parameters
    ----------
        conn : sqlite3.Connection
            database
        table : string
            target table

    Returns
    -------
        list(dict)
            list of records
    """
    with conn:
        elems = conn.execute(f"SELECT * FROM {table} WHERE 1 = 1")
        available = elems.fetchall()
    # deserialize the thing
    fs = fields(conn, table)
    return [deserialize(a, fs) for a in available]
