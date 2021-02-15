# -*- coding: utf-8 -*-
"""
Actually using ``String`` it's pointless, since SQLite has only one text type
and it is ``TEXT``, and the maximum length is coherently ignored by SQLite.
Nevertheless the information is stored in the DB, even if the DBMS won't use it,
so we can keep declaring a size for fields where it matters.

Same considerations apply to datetime, with the further gain that SQLite it's
storing as he wish but able to use some dedicated functions.
"""

import sqlalchemy
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base


class MyBase:
    uid = Column(Integer, primary_key=True, unique=True)
    hash = Column(String(64), unique=True)
    # TODO: should we use `func.utcnow`?
    # https://stackoverflow.com/a/33532154/8653979
    ctime = Column(DateTime(timezone=True), server_default=func.now())
    mtime = Column(DateTime(timezone=True), onupdate=func.now())


Base = declarative_base(cls=MyBase)


class Theory(Base):
    __tablename__ = "theories"
    pto = Column(Integer)


# mixin
class CalcResult:
    external = Column(Text)
    t_hash = Column(String(64))
    o_hash = Column(String(64))
    pdf = Column(Text)


class Cache(CalcResult, Base):
    __tablename__ = "cache"
    result = Column(Text)


class Log(CalcResult, Base):
    __tablename__ = "logs"
    log = Column(Text)


# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = sqlalchemy.create_engine("sqlite:///sqlalchemy_example.db")

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
