# -*- coding: utf-8 -*-
import abc
import datetime as dt
import textwrap

import numpy as np
import pandas as pd
import pendulum
import sqlalchemy.orm

from .. import cfg
from ..data import db, dfdict
from . import table_manager as tm

# define some shortcuts
t = "t"
o = "o"
c = "c"
l = "l"

table_objects = dict(t=db.Theory, c=db.Cache, l=db.Log)


class NavigatorApp(abc.ABC):
    """
    Navigator base class holding all elementry operations.

    Parameters
    ----------
        cfgpath : dict
            path to banana configuration
        external : string
            mode identifier
    """

    myname = "banana"
    table_objects = table_objects
    hash_len = 6

    def __init__(self, cfgpath, external=None):
        self.cfg = cfg.load(cfgpath)
        self.external = external
        db_path = self.cfg["paths"]["database"]
        self.session = sqlalchemy.orm.sessionmaker(db.engine(db_path))()
        # read input
        self.input_tables = {}
        for table in self.cfg["input"]["tables"]:
            self.input_tables[table] = tm.TableManager(
                self.session, self.table_objects[table[0]]
            )
        # load logs
        self.logs = tm.TableManager(self.session, db.Log)

    def change_external(self, external):
        """
        Change mode

        Parameters
        ----------
            mode : string
                mode identifier
        """
        self.external = external

    def table_name(self, table_abbrev):
        """
        Expand a table short cut to its full name

        Parameters
        ----------
            table_abbrev : str
                short cut

        Returns
        -------
            name : str
                full name
        """
        if table_abbrev == "logs"[: len(table_abbrev)]:
            return "logs"
        for tab in self.input_tables:
            if table_abbrev == tab[: len(table_abbrev)]:
                return tab
        raise ValueError(f"Unknown table {table_abbrev}")

    def table_manager(self, table):
        """Get corresponding TableManager

        Parameters
        ----------
        table : str
            table identifier

        Returns
        -------
        tm : yadmark.table_manager.TableManager
            corresponding TableManager

        """
        # logs?
        tn = self.table_name(table)
        if tn == "logs":
            return self.logs
        # input table
        return self.input_tables[tn]

    def get(self, table, doc_id):
        """Table getter wrapper.

        Parameters
        ----------
        table : str
            table identifier
        doc_id : int or str
            it can be: a :class:`str` interpreted as partial hash
            (:func:`banana.data.sql.select_by_hash`), a non-negative
            :class:`int` interpreted as the record unique identifier
            (:func:`banana.data.sql.select_by_uid`), a negative :class:`int`
            interpreted as record position
            (:func:`banana.data.sql.select_by_position`)

        Returns
        -------
        dict
            the retrieved document

        """
        return self.table_manager(table).get(doc_id)

    def get_by_log(self, table, log_id):
        """Get card related to given log.

        Parameters
        ----------
        table : str
            table identifier (of the table from which to get the final card)
        log_id : int or str
            document identifier of the chosen log, see :meth:`get`

        Returns
        -------
        dict
            the retrieved document

        """
        log = self.table_manager(l).get(log_id)

        return self.table_manager(table).get(log[f"{table[0]}_hash"])

    def get_all(self, table):
        """Get full table.

        Parameters
        ----------
        table : str
            table identifier

        Returns
        -------
        list(dict)
            the full list of documents in the table

        """
        return self.table_manager(table).all()

    def list_all(self, table, input_data=None):
        """List all elements in a nice table

        Parameters
        ----------
        table : string
            table identifier
        input_data : list
            data to list

        Returns
        -------
        df : pandas.DataFrame
            list

        """
        # collect
        if input_data is None:
            input_data = self.get_all(table)
        data = []
        for el in input_data:
            # obj = {"hash": el["hash"][:6]}
            obj = {"uid": el["uid"]}
            obj["hash"] = el["hash"][: self.hash_len]
            self.__getattribute__(f"fill_{self.table_name(table)}")(el, obj)
            obj["ctime"] = (
                pendulum.duration(
                    seconds=(dt.datetime.utcnow() - el["ctime"]).total_seconds()
                )
                .in_words(separator="@")
                .split("@")[0]
            )
            data.append(obj)
        # output
        df = pd.DataFrame(data)
        # if empty, no column is present as well
        if len(df) > 0:
            df.set_index("uid", inplace=True)
        return df

    def show_full_logs(self, t_fields=None, o_fields=None, keep_hashes=False):
        """Show additional, associated fields in the logs (JOIN).

        Parameters
        ----------
        t_fields : list
            theory fields
        o_fields : list
            ocard fields
        keep_hashes : boolean
            display hashes?

        Returns
        -------
        df : pandas.DataFrame
            data frame

        """
        # apply some defaults
        if t_fields is None:
            t_fields = []
        if o_fields is None:
            o_fields = []

        # collect external data
        theories_df = pd.DataFrame(self.get_all(t))
        if len(theories_df) > 0:
            theories = theories_df[["hash"] + t_fields]
            theories = theories.rename(columns={"hash": "theory"})
        else:
            theories = theories_df
        ocards_df = pd.DataFrame(self.get_all(o))
        if len(theories_df) > 0:
            ocards = ocards_df[["hash"] + o_fields]
            ocards = ocards.rename(columns={"hash": "ocard"})
        else:
            ocards = ocards_df

        # get my data and merge
        logs = self.list_all(l)
        if len(logs) > 0:
            logs.reset_index(inplace=True)
            if len(theories) > 0:
                logs = logs.merge(theories, on="theory")
            if len(ocards) > 0:
                logs = logs.merge(ocards, on="ocard")
            logs.set_index("uid", inplace=True)

            # move ctime at the end
            columns = logs.columns.tolist()
            columns.remove("ctime")
            logs = logs[columns + ["ctime"]]

            # drop hashes, if not denied
            if not keep_hashes:
                logs = logs.drop(["theory", "ocard"], axis=1)

            # sort on uid
            logs.sort_index(inplace=True)

        return logs

    def cache_as_dfd(self, doc_id):
        """Load all structure functions in log as DataFrame

        Parameters
        ----------
        doc_id : str or int
            document identifier, see :meth:`get`

        Returns
        -------
        log : DFdict
            DataFrames

        """
        cache = self.get(c, doc_id)

        res = cache["result"]

        dfd = dfdict.DFdict()
        for k, v in res.items():
            dfd[k] = pd.DataFrame(v)

        dfd.print(
            textwrap.dedent(
                f"""
                - theory: `{cache['t_hash']}`
                - obs: `{cache['o_hash']}`
                - using PDF: *{cache['pdf']}*\n"""
            ),
            position=0,
        )
        dfd.external = cache["external"]

        return dfd

    def log_as_dfd(self, doc_id):
        """Load all structure functions in log as DataFrame

        Parameters
        ----------
        doc_id : str or int
            document identifier, see :meth:`get`

        Returns
        -------
        log : DFdict
            DataFrames

        """
        log = self.get(l, doc_id)

        dfd = log["log"]
        dfd.print(
            textwrap.dedent(
                f"""
                - theory: `{log['t_hash']}`
                - obs: `{log['o_hash']}`
                - using PDF: *{log['pdf']}*\n"""
            ),
            position=0,
        )

        return dfd

    @staticmethod
    def load_dfd(dfd, retrieve_method):
        if isinstance(dfd, dfdict.DFdict):
            log = dfd
            id_ = "not-an-id"
        else:
            log = retrieve_method(dfd)
            id_ = dfd

        if log is None:
            raise ValueError(f"Log id: '{id_}' not found")

        return id_, log

    def list_all_similar_logs(self, doc_id):
        """List logs with similar input.

        Search logs which are similar to the one given, i.e., same theory and,
        same observable, and same pdfset.

        Parameters
        ----------
        doc_id : str or int
            document identifier, see :meth:`get`

        Returns
        -------
        df : pandas.DataFrame
            created frame

        Note
        ----
        The external it's not used to discriminate logs: even different
        externals should return the same numbers, so it's relevant to keep all
        of them.

        """
        # obtain reference log
        ref_log = self.get(l, doc_id)

        related_logs = []
        all_logs = self.get_all(l)

        for lg in all_logs:
            if lg["t_hash"] != ref_log["t_hash"]:
                continue
            if lg["o_hash"] != ref_log["o_hash"]:
                continue
            if lg["pdf"] != ref_log["pdf"]:
                continue
            related_logs.append(lg)

        return self.list_all(l, related_logs)

    def subtract_tables(self, dfd1, dfd2):
        """Subtract comparison tables.

        Subtract results in the second table from the first one,
        properly propagate the integration error and recompute the relative
        error on the subtracted results.

        Parameters
        ----------
        dfd1 : dict or hash
            if hash the doc_hash of the log to be loaded
        dfd2 : dict or hash
            if hash the doc_hash of the log to be loaded

        Returns
        -------
        diffout : DFdict
            created frames

        """
        # load json documents
        id1, log1 = self.load_dfd(dfd1, self.log_as_dfd)
        id2, log2 = self.load_dfd(dfd2, self.log_as_dfd)

        # print head
        diffout = dfdict.DFdict()
        msg = f"**Subtracting** id: `{id1}` - id: `{id2}`, in table *logs*"
        diffout.print(msg, "-" * len(msg), sep="\n")
        diffout.print()

        # iterate observables
        for obs in log1.keys():
            if obs[0] == "_":
                continue
            if obs not in log2:
                print(f"{obs}: not matching in log2")
                continue

            # load observable tables
            table1 = pd.DataFrame(log1[obs])
            table2 = pd.DataFrame(log2[obs])

            # check for compatible kinematics
            if any([any(table1[y] != table2[y]) for y in ["x", "Q2"]]):
                raise ValueError("Cannot compare tables with different (x, Q2)")

            # subtract and propagate
            known_col_set = {
                "x",
                "Q2",
                self.myname,
                f"{self.myname}_error",
                "percent_error",
            }
            t1_ext = list(set(table1.keys()) - known_col_set)[0]
            t2_ext = list(set(table2.keys()) - known_col_set)[0]
            if t1_ext == t2_ext:
                tout_ext = t1_ext
            else:
                tout_ext = f"{t2_ext}-{t1_ext}"
            table_out = table1.copy()
            table_out.rename(columns={t1_ext: tout_ext}, inplace=True)
            table_out[tout_ext] = table1[t1_ext] - table2[t2_ext]
            # subtract our values
            table_out[self.myname] -= table2[self.myname]
            table_out[f"{self.myname}_error"] += table2[f"{self.myname}_error"]

            # compute relative error
            def rel_err(row, tout_ext=tout_ext):
                if row[tout_ext] == 0.0:
                    if row[self.myname] == 0.0:
                        return 0.0
                    return np.nan
                else:
                    return (row[self.myname] / row[tout_ext] - 1.0) * 100

            table_out["percent_error"] = table_out.apply(rel_err, axis=1)

            # dump results' table
            diffout[obs] = table_out

        return diffout

    def compare_external(self, dfd1, dfd2):
        """Compare two results in the cache.

        It's taking two results from external benchmarks and compare them in a
        single table.

        Parameters
        ----------
        dfd1 : dict or hash
            if hash the doc_hash of the cache to be loaded
        dfd2 : dict or hash
            if hash the doc_hash of the cache to be loaded

        """
        # load json documents
        id1, cache1 = self.load_dfd(dfd1, self.cache_as_dfd)
        id2, cache2 = self.load_dfd(dfd2, self.cache_as_dfd)

        if cache1.external == cache2.external:
            cache1.external = f"{cache1.external}1"
            cache2.external = f"{cache2.external}2"

        # print head
        cache_diff = dfdict.DFdict()
        msg = f"**Comparing** id: `{id1}` - id: `{id2}`, in table *cache*"
        cache_diff.print(msg, "-" * len(msg), sep="\n")
        cache_diff.print(f"- *{cache1.external}*: `{id1}`")
        cache_diff.print(f"- *{cache2.external}*: `{id2}`")
        cache_diff.print()

        for obs in cache1.keys():
            if obs not in cache2:
                print(f"{obs}: not matching in log2")
                continue

            # load observable tables
            table1 = pd.DataFrame(cache1[obs])
            table2 = pd.DataFrame(cache2[obs])
            table_out = table1.copy()

            # check for compatible kinematics
            if any([any(table1[y] != table2[y]) for y in ["x", "Q2"]]):
                raise ValueError("Cannot compare tables with different (x, Q2)")

            table_out.rename(columns={"result": cache1.external}, inplace=True)
            table_out[cache2.external] = table2["result"]

            # compute relative error
            def rel_err(row, t1_ext=cache1.external, t2_ext=cache2.external):
                if row[t2_ext] == 0.0:
                    if row[t1_ext] == 0.0:
                        return 0.0
                    return np.nan
                else:
                    return (row[t1_ext] / row[t2_ext] - 1.0) * 100

            table_out["percent_error"] = table_out.apply(rel_err, axis=1)

            # dump results' table
            cache_diff[obs] = table_out

        return cache_diff

    @staticmethod
    @abc.abstractmethod
    def is_valid_physical_object(name):
        """Identifies physical objects.

        Used to test names, in order to distinguish physical quantities from
        metadata.

        Parameters
        ----------
        name: str
            name to test

        Returns
        -------
        bool
            test response

        """

    def crashed_log(self, doc_id):
        """Check if the log passed the default assertions.

        Parameters
        ----------
        doc_id : str or int
            document identifier, see :meth:`get`

        Returns
        -------
        cdfd : dict
            log without kinematics

        """
        dfd = self.log_as_dfd(doc_id)

        if "_crash" not in dfd:
            raise ValueError("log didn't crash!")

        cdfd = {}
        for name, df in dfd.items():
            if self.is_valid_physical_object(name):
                cdfd[name] = f"{len(df)} points"
            else:
                cdfd[name] = dfd[name]

        return cdfd

    def truncate(self, table):
        """Empty chosen table

        Parameters
        ----------
        table: str
            table identifier

        """
        self.table_manager(table).truncate()

    def remove(self, table, records):
        """Remove chosen elements from given table

        Parameters
        ----------
        table: str
            table identifier
        records: list(str or int or dict)
            records to remove, specified as:

            - :class:`str`: partial hash
            - :class:`int`, ``>=0``: uid
            - :class:`int`, ``<0``: position from the end of the table
            - :class:`dict`: the record itself

        """
        self.table_manager(table).remove(records)
