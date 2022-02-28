# -*- coding: utf-8 -*-
import pathlib

import pytest
import sqlalchemy
import sqlalchemy.orm
import yaml
from sqlalchemy.ext.declarative import declarative_base

from banana import navigator
from banana.data import db
from banana.navigator import table_manager as tm


class FakeNavApp(navigator.navigator.NavigatorApp):
    def __init__(self, session, cfgpath, external=None, extra_tables=None):
        super().__init__(cfgpath, external)

        self.session = session

        if extra_tables is None:
            extra_tables = {}
        self.input_tables = {**self.input_tables, **extra_tables}

    def fill_ciao(self, theo, obj):
        obj["name"] = theo["name"]

    def is_valid_physical_object(_name):
        return True


class TestNavigatorApp:
    def test_change_external(self, banana_yaml, dbsession):
        app = FakeNavApp(dbsession, banana_yaml, "test")

        assert app.external == "test"

        app.change_external("comeva")
        assert app.external == "comeva"

    def test_get(self, banana_yaml, dbsession, tab_ciao):
        tabman = tm.TableManager(dbsession, tab_ciao)
        app = FakeNavApp(dbsession, banana_yaml, "test", extra_tables=dict(ciao=tabman))

        recs = app.get_all("ciao")
        assert len(recs) == 0

        newrec = tab_ciao(uid=42, name="leorio", hash="abcdef123456789")
        with dbsession.begin():
            dbsession.add(newrec)
        recs = app.get_all("ciao")
        assert len(recs) == 1
        assert isinstance(recs[0], dict)

        rec = app.get("ciao", "a")
        for key, value in rec.items():
            if key != "atime":
                assert value == getattr(newrec, key)
            else:
                assert value != getattr(newrec, key)

    def test_list_all(self, banana_yaml, dbsession, tab_ciao):
        tabman = tm.TableManager(dbsession, tab_ciao)
        app = FakeNavApp(dbsession, banana_yaml, "test", extra_tables=dict(ciao=tabman))

        df = app.list_all("ciao")
        assert len(df) == 0

        with dbsession.begin():
            newrec = tab_ciao(uid=42, name="leorio", hash="abcdef123456789")
            dbsession.add(newrec)
        df = app.list_all("ciao")
        assert len(df) == 1

    def test_table_name(self, banana_yaml, dbsession, tab_ciao):
        tabman = tm.TableManager(dbsession, tab_ciao)
        app = FakeNavApp(dbsession, banana_yaml, "test", extra_tables=dict(ciao=tabman))

        assert app.table_name("l") == "logs"
        assert app.table_name("c") == "ciao"

        with pytest.raises(ValueError):
            app.list_all("b")

    def test_table_manager(self, banana_yaml, dbsession, tab_ciao):
        tabman = tm.TableManager(dbsession, tab_ciao)
        app = FakeNavApp(dbsession, banana_yaml, "test", extra_tables=dict(ciao=tabman))

        assert app.table_manager("l") == app.logs

    def test_delete(self, banana_yaml, dbsession, tab_ciao, monkeypatch):
        tabman = tm.TableManager(dbsession, tab_ciao)
        app = FakeNavApp(dbsession, banana_yaml, "test", extra_tables=dict(ciao=tabman))

        df = app.list_all("ciao")
        assert len(df) == 0

        with dbsession.begin():
            newrecs = [
                tab_ciao(uid=i, name="leorio", hash="abcdef123456789")
                for i in range(10)
            ]
            dbsession.add_all(newrecs)

        df = app.list_all("ciao")
        assert len(df) == 10

        app.remove("ciao", [0, 1])
        df = app.list_all("ciao")
        assert len(df) == 8

        monkeypatch.setattr("builtins.input", lambda _: "n")
        app.truncate("ciao")
        df = app.list_all("ciao")
        assert len(df) == 8

        monkeypatch.setattr("builtins.input", lambda _: "y")
        app.truncate("ciao")
        df = app.list_all("ciao")
        assert len(df) == 0


Base = declarative_base(cls=db.MyBase)


class Theory(Base):
    __tablename__ = "theories"
    PTO = sqlalchemy.Column(sqlalchemy.Integer)


class OCard(Base):
    __tablename__ = "ocards"
    process = sqlalchemy.Column(sqlalchemy.Integer)


class Cache(Base):
    __tablename__ = "cache"
    t_hash = sqlalchemy.Column(sqlalchemy.String(64))
    o_hash = sqlalchemy.Column(sqlalchemy.String(64))
    pdf = sqlalchemy.Column(sqlalchemy.Text)
    result = sqlalchemy.Column(sqlalchemy.Text)


class Log(Base):
    __tablename__ = "logs"
    t_hash = sqlalchemy.Column(sqlalchemy.String(64))
    o_hash = sqlalchemy.Column(sqlalchemy.String(64))
    pdf = sqlalchemy.Column(sqlalchemy.Text)
    log = sqlalchemy.Column(sqlalchemy.Text)


class NavApp(navigator.navigator.NavigatorApp):
    def __init__(self, cfgpath, external=None):
        super().__init__(cfgpath, external)
        for tab in [Theory, OCard, Cache]:
            self.input_tables[tab.__tablename__] = tm.TableManager(self.session, tab)
        self.logs = tm.TableManager(self.session, Log)

    def is_valid_physical_object(_name):
        return True


@pytest.fixture
def benchsession(banana_yaml):
    "Setup banana database (with benchmark scheme)"
    db_path = yaml.safe_load(banana_yaml.read_text())["paths"]["database"]

    engine = sqlalchemy.create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine

    with sqlalchemy.orm.Session(bind=engine) as session:
        yield session

    pathlib.Path(db_path).unlink()


@pytest.fixture
def benchnav(banana_yaml):
    "Setup banana database (with benchmark scheme)"
    app = NavApp(banana_yaml, "test")

    yield app


class TestNavigatorAppSchemeDependent:
    def test_show_full_logs(self, banana_yaml, benchsession, benchnav):
        benchnav.show_full_logs()
