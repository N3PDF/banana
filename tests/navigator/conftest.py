# -*- coding: utf-8 -*-
import datetime
import pathlib

import pytest
import sqlalchemy
import sqlalchemy.orm
import yaml
from sqlalchemy.ext.declarative import declarative_base


class MyBase:
    uid = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, unique=True)


Base = declarative_base(cls=MyBase)


class Ciao(Base):
    __tablename__ = "ciao"
    name = sqlalchemy.Column(sqlalchemy.String)
    hash = sqlalchemy.Column(sqlalchemy.String)
    ctime = sqlalchemy.Column(sqlalchemy.DateTime(), default=datetime.datetime.utcnow)
    atime = sqlalchemy.Column(sqlalchemy.DateTime(), default=datetime.datetime.utcnow)


@pytest.fixture
def tab_ciao():
    yield Ciao


@pytest.fixture
def dbsession(banana_yaml):
    "Setup banana database"
    db_path = yaml.safe_load(banana_yaml.read_text())["paths"]["database"]

    engine = sqlalchemy.create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine

    with sqlalchemy.orm.Session(bind=engine) as session:
        yield session

    pathlib.Path(db_path).unlink()
