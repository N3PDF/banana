# -*- coding: utf-8 -*-
import pickle
import hashlib
import copy

mapping = {
    int: "INTEGER",
    float: "REAL",
    str: "TEXT",
    dict: "BLOB",
    list: "BLOB",
    bytes: "BLOB",
    bool: "BOOL",
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
    blobbed_types = [list, dict]
    sorted_data = dict(sorted(data.items()))
    ndata = []
    for d in sorted_data.values():
        if type(d) in blobbed_types:
            ndata.append(pickle.dumps(d))
        else:
            ndata.append(d)
    return tuple(ndata)


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


# db interface
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
