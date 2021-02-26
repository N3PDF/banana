# -*- coding: utf-8 -*-
from datetime import timezone
import abc

import sqlalchemy.orm
import pandas as pd
from human_dates import human_dates

from ..data import db
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
        cfg : dict
            banana configuration
        external : string
            mode identifier
    """

    table_objects = table_objects
    hash_len = 6

    def __init__(self, banana_cfg, external=None):
        self.cfg = banana_cfg
        self.external = external
        db_path = self.cfg["database_path"]
        self.session = sqlalchemy.orm.sessionmaker(db.engine(db_path))()
        # read input
        self.input_tables = {}
        for table in self.cfg["input_tables"]:
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
        """
        Get corresponding TableManager

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

    def get(self, table, doc_id=None):
        """
        Getter wrapper.

        Parameters
        ----------
            table : str
                table identifier
            doc_id : None or int
                if given, retrieve single document

        Returns
        -------
            df : pandas.DataFrame
                created frame
        """
        # list all
        tab_m = self.table_manager(table)

        if doc_id is None:
            return tab_m.all()

        return tab_m.get(doc_id)

    def list_all(self, table, input_data=None):
        """
        List all elements in a nice table

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
            input_data = self.get(table)
        data = []
        for el in input_data:
            # obj = {"hash": el["hash"][:6]}
            obj = {"uid": el["uid"]}
            obj["hash"] = el["hash"][: self.hash_len]
            self.__getattribute__(f"fill_{self.table_name(table)}")(el, obj)
            # datetime is saved in UTC, in order to convert:
            #  - make datetime object aware of timezone
            #  - update timezone to local
            #  - cast to naïve timezone again
            # TODO: lift the former steps in human_dates
            obj["ctime"] = human_dates(
                el["ctime"]
                .replace(tzinfo=timezone.utc)
                .astimezone()
                .replace(tzinfo=None)
            )
            data.append(obj)
        # output
        df = pd.DataFrame(data)
        return df
