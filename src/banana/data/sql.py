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
    bool: "BOOL",
}
"""
Mapping of Python types to SQLite types.
"""


def create_table(name, obj):
    """
    SQL command for creating the table

    Parameters
    ----------
        name : str
            table name
        obj : dict
            column-names to example values mapping

    Returns
    -------
        tmpl : str
            SQL command
    """
    tmpl = f"""
    CREATE TABLE {name} (
        uid INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        hash BLOB UNIQUE,
    """

    for k, v in obj.items():
        tmpl += f"    {k} {mapping[type(v)]},\n"

    tmpl = tmpl[:-2]

    tmpl += """);"""

    return tmpl


def serialize(data):
    """
    Eventually turn some elements into their binary representation

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
        raw_records : list(dict)
            list of all dictionaries
        records : list(tuple)
            all records ready for insertion
        fields : list(str)
            all fields ready for insertion
    """
    records = []
    raw_records = []
    for upd in updates:
        record = copy.copy(base)
        record.update(upd)
        raw_records.append(record)
        serialized_record = serialize(record)
        hashed_record = add_hash(serialized_record)
        records.append(hashed_record)
    return (raw_records, records, list(base.keys()) + ["hash"])


def insert(conn, table, fields, records):
    """
    Insert all records into the DB.

    Parameters
    ----------
        conn : sqlite3.Connection
            database
        table : string
            target table
        raw_fields : list
            list with all original fields
        records : list
            list with all records
    """
    tmpl = (
        f"INSERT INTO {table}("
        + ",".join(fields)
        + ") VALUES ("
        + ",".join(list("?" * len(fields)))
        + ")"
    )
    with conn:
        conn.executemany(tmpl, records)
