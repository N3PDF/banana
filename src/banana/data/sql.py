# -*- coding: utf-8 -*-
import pickle
import hashlib
import copy
import sqlite3

import pandas as pd

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


def create_table(table):
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
    tmpl = f"CREATE TABLE {table.name} (\n"
    # collect
    tmpl += ",\n".join(table.fields)
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
    return (documents, pd.DataFrame(records, columns=(list(base.keys()) + ["hash"])))


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


def insertmany(session, table, df):
    """
    Insert all records into the DB.

    Parameters
    ----------
    session : sqlalchemy.session.Session
        database
    table : sqlalchemy.types.Type
        target table
    df : pandas.DataFrame
        dataframe all records
    """
    session.bulk_insert_mappings(table, df.to_dict(orient="records"))
    # TODO: do we want to commit here or somewhere else?
    session.commit()


def insertnew(session, table, df):
    """
    Insert all records that do not exist yet (determined by hash).


    Parameters
    ----------
    session : sqlalchemy.session.Session
        database
    table : sqlalchemy.types.Type
        target table
    df : pandas.DataFrame
        dataframe all records
    """
    hashes = session.query(table.hash).all()
    new_records = df[~df["hash"].isin(hashes)]
    insertmany(session, table, df)


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
