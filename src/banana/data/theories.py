# -*- coding: utf-8 -*-
import pathlib

import yaml

from . import db, sql

_here = pathlib.Path(__file__).parent

# load default theory
default_card = {}
with open(_here / "theory_template.yaml") as f:
    default_card = yaml.safe_load(f)
default_card = dict(sorted(default_card.items()))

# db interface
def load(session, updates):
    # add hash
    raw_records, df = sql.prepare_records(default_card, updates)
    # insert new ones
    sql.insertnew(session, db.Theory, df)
    return raw_records
