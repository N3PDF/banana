# -*- coding: utf-8 -*-
from datetime import datetime
import abc

import pandas as pd
from human_dates import human_dates

from .. import mode_selector
from . import table_manager as tm

# define some shortcuts
t = "t"
o = "o"
c = "c"
l = "l"


class NavigatorApp(mode_selector.ModeSelector, abc.ABC):
    """
    Navigator base class holding all elementry operations.

    Parameters
    ----------
        cfg : dict
            banana configuration
        mode : string
            mode identifier
    """

    def __init__(self, cfg, mode):
        super().__init__(cfg, mode)
        self.cfg = cfg
        # read input
        self.input_tables = {}
        for table in self.cfg["input_tables"]:
            self.input_tables[table] = tm.TableManager(self.idb.table(table))
        # load logs
        self.logs = tm.TableManager(self.odb.table("logs"))

    def change_mode(self, mode):
        """
        Change mode

        Parameters
        ----------
            mode : string
                mode identifier
        """
        self.__init__(self.cfg, mode)

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
        t_m = self.table_manager(table)
        if doc_id is None:
            return t_m.all()
        return t_m.get(doc_id)

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
            obj = {"doc_id": el.doc_id}
            self.__getattribute__(f"fill_{self.table_name(table)}")(el, obj)
            dt = datetime.fromisoformat(el["_created"])
            obj["created"] = human_dates(dt)
            data.append(obj)
        # output
        df = pd.DataFrame(data)
        return df
