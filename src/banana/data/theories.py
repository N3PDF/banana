# -*- coding: utf-8 -*-
import pathlib

import yaml

_here = pathlib.Path(__file__).parent

# load default theory
default_theory = {}
with open(_here / "theory_template.yaml") as f:
    default_theory = yaml.safe_load(f)

def create_table():
    """
    SQL command for creating the theories table

    Returns
    -------
        sql : str
            SQL command
    """
    sql_tmpl = """
    CREATE TABLE theories (
        uid INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    """

    sql_mapping = {
        int: "INTEGER",
        float: "REAL",
        str: "TEXT"
    }

    for k,v in default_theory.items():
        sql_tmpl += f"    {k} {sql_mapping[type(v)]},\n"

    sql_tmpl = sql_tmpl[:-2]

    sql_tmpl += """);"""

    return sql_tmpl