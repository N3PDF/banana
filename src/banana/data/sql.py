# -*- coding: utf-8 -*-
import copy
import hashlib
import pickle
import numpy as np

import pandas as pd
import sqlalchemy.sql

from banana.data import dfdict


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
    blobbed_types = [list, dict, dfdict.DFdict, np.ndarray]
    sorted_data = dict(sorted(data.items()))
    ndata = []
    for d in sorted_data.values():
        if type(d) in blobbed_types:
            ndata.append(pickle.dumps(d))
        else:
            ndata.append(d)
    return tuple(ndata)


def deserialize(data):
    """
    Undo the binary representation.

    Parameters
    ----------
        data : list
            raw data

    Returns
    -------
        obj : dict
            composed object
    """
    obj = {}
    for f, el in data.__dict__.items():
        if f[0] == "_":
            continue
        if isinstance(el, bytes):
            obj[f] = pickle.loads(el)
            if isinstance(obj[f], dict) and "__msgs__" in obj[f]:
                obj[f] = dfdict.DFdict.from_document(obj[f])
        else:
            obj[f] = el
    return obj


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
    return (*record, h.digest().hex())


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
    # TODO: why the hash field is a 1-tuple?
    hashes = [h[0] for h in session.query(table.hash).all()]
    new_records = df[~df["hash"].isin(hashes)]
    insertmany(session, table, new_records)


class HashError(KeyError):
    def __init__(self, descr, hashes=None):
        if hashes is not None:
            msg = "the following hashes have been found:"
            msg += "\n- " + "\n- ".join(hashes) + "\n"
            print(msg)
        super().__init__(descr)


def select_hash(session, table_object, hash_partial):
    """
    Find a record by its hash.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        DB ORM session
    table_object : sqlalchemy.ext.declarative.api.DeclarativeMeta
        table object
    hash_partial : str
        hash identifier

    Returns
    -------
    dict
        record
    """
    available = (
        session.query(table_object)
        .filter(
            sqlalchemy.sql.func.substr(table_object.hash, 1, len(hash_partial))
            == hash_partial
        )
        .all()
    )
    # too much?
    if len(available) > 1:
        raise HashError("hash is not unique", [a.hash for a in available])
    elif len(available) < 1:
        raise HashError("hash not found")
    # deserialize the thing
    return deserialize(available[0])


def select_all(session, table_object):
    """
    Collect all records.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
        DB ORM session
    table_object : sqlalchemy.ext.declarative.api.DeclarativeMeta
        table object

    Returns
    -------
    list(dict)
        list of records
    """
    available = session.query(table_object).all()
    return [deserialize(a) for a in available]
