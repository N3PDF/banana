import pathlib

import pytest
import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.ext.declarative import declarative_base

from banana.data import theories


class MyBase:
    uid = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, unique=True)
    hash = sqlalchemy.Column(sqlalchemy.String(64), unique=True)


Base = declarative_base(cls=MyBase)


class Theory(Base):
    __tablename__ = "theories"
    ciao = sqlalchemy.Column(sqlalchemy.String)
    blub = sqlalchemy.Column(sqlalchemy.String)


@pytest.fixture
def dbsession(tmp_path, monkeypatch):
    "Setup banana database"
    monkeypatch.setattr("banana.data.db.Theory", Theory)

    path = pathlib.Path(tmp_path) / "test.db"

    engine = sqlalchemy.create_engine(f"sqlite:///{path}")
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine

    with sqlalchemy.orm.Session(bind=engine) as session:
        yield session

    pathlib.Path(path).unlink()


def test_default():
    default = theories.default_card

    assert isinstance(default, dict)
    assert default["ModEv"] == "EXA"
    assert default["FNS"] == "FFNS"
    assert default["XIF"] == 1.0


def test_load(dbsession, monkeypatch):
    default = dict(ciao="Gon", blub="bla")
    monkeypatch.setattr("banana.data.theories.default_card", default)

    come = "come va?"
    with dbsession.begin():
        loaded = theories.load(dbsession, [dict(ciao=come)])[0]

    assert loaded["ciao"] == come
    assert loaded["blub"] == "bla"
