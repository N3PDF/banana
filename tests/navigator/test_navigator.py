# -*- coding: utf-8 -*-
import pathlib
import pickle

import pytest
import sqlalchemy
import sqlalchemy.orm
import yaml
from sqlalchemy.ext.declarative import declarative_base

from banana import navigator
from banana.data import db, dfdict
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

    @staticmethod
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

    def test_load_dfd(self, dbsession, banana_yaml):
        app = FakeNavApp(dbsession, banana_yaml, "test")

        ciao, come = app.load_dfd("ciao", lambda _dfd: "come va")
        assert ciao == "ciao"
        assert come == "come va"

        dfd = dfdict.DFdict()
        id_, retdfd = app.load_dfd(dfd, lambda _dfd: "come va")
        assert id_ == "not-an-id"
        assert retdfd is dfd

        with pytest.raises(ValueError, match="not found"):
            _ = app.load_dfd("ciao", lambda _dfd: None)


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
    external = sqlalchemy.Column(sqlalchemy.Text)
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

    def fill_logs(self, lg, obj):
        obj["theory"] = lg["t_hash"]
        obj["ocard"] = lg["o_hash"]
        obj["pdf"] = lg["pdf"]

    @staticmethod
    def is_valid_physical_object(name):
        return name != "False"


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


class MyLog(dict):
    text = ""

    def print(self, text, position=-1):
        self.text += text + f"position={position}"


class TestNavigatorAppSchemeDependent:
    def test_show_full_logs(self, banana_yaml, benchsession, benchnav):
        logs = benchnav.show_full_logs()

        assert len(logs) == 0

        with benchsession.begin():
            newt = Theory(uid=42, PTO=7, hash="abc")
            benchsession.add(newt)
            newo = OCard(uid=21, process=0, hash="def")
            benchsession.add(newo)
            newl = Log(
                uid=17, t_hash="abc", o_hash="def", pdf="NNPDF", hash="123456789"
            )
            benchsession.add(newl)

        assert len(benchnav.get_all("theories")) == 1
        assert len(benchnav.get_all("ocards")) == 1
        assert len(benchnav.get_all("logs")) == 1

        logs = benchnav.show_full_logs(["PTO"], ["process"])
        assert len(logs) == 1
        assert logs["PTO"][17] == 7
        assert logs["process"][17] == 0
        assert logs["pdf"][17] == "NNPDF"

    def test_get_by_log(self, banana_yaml, benchsession, benchnav):
        with benchsession.begin():
            newt = Theory(uid=42, PTO=31, hash="abc")
            benchsession.add(newt)
            newo = OCard(uid=21, process=0, hash="def")
            benchsession.add(newo)
            newl = Log(
                uid=17, t_hash="abc", o_hash="def", pdf="NNPDF", hash="123456789"
            )
            benchsession.add(newl)

        th = benchnav.get_by_log("t", "1234")
        assert th["PTO"] == 31

    def test_as_dfd(self, banana_yaml, benchsession, benchnav):
        with benchsession.begin():
            newt = Theory(uid=42, PTO=31, hash="abc")
            benchsession.add(newt)
            newo = OCard(uid=21, process=0, hash="def")
            benchsession.add(newo)
            newc = Cache(
                uid=17,
                t_hash="abc",
                o_hash="def",
                pdf="NNPDF",
                hash="123456789",
                result=pickle.dumps({"table": [{"column": "value"}]}),
                external="blub",
            )
            benchsession.add(newc)
            newl = Log(
                uid=17,
                t_hash="abc",
                o_hash="def",
                pdf="NNDPF",
                hash="9876654321",
                log=pickle.dumps(MyLog()),
            )
            benchsession.add(newl)

        cache = benchnav.cache_as_dfd("1234")
        assert cache.external == "blub"
        assert cache["table"]["column"][0] == "value"

        log = benchnav.log_as_dfd("9876")
        assert "position=0" in log.text
        for field in ["theory", "obs", "PDF"]:
            assert field in log.text

    def test_simlogs(self, banana_yaml, benchsession, benchnav):
        with benchsession.begin():
            newt = Theory(uid=42, PTO=31, hash="abc")
            benchsession.add(newt)
            newo = OCard(uid=21, process=0, hash="def")
            benchsession.add(newo)

            def newl(uid, th="abc", oh="def", pdf="NNPDF"):
                return Log(
                    uid=uid,
                    t_hash=th,
                    o_hash=oh,
                    pdf=pdf,
                    hash=str(uid),
                    log=pickle.dumps(MyLog()),
                )

            benchsession.add_all([newl(5), newl(50), newl(55)])
            benchsession.add(newl(4, th="alskdjflk"))
            benchsession.add(newl(3, oh="lasdjflk"))
            benchsession.add(newl(2, pdf="NNDPF"))

        simlogs = benchnav.list_all_similar_logs(5)
        assert len(simlogs) == 3
        assert sorted(simlogs["hash"].values) == ["5", "50", "55"]

    def test_crashed(self, banana_yaml, benchsession, benchnav):
        with benchsession.begin():
            newt = Theory(uid=42, PTO=31, hash="abc")
            benchsession.add(newt)
            newo = OCard(uid=21, process=0, hash="def")
            benchsession.add(newo)
            working_log = MyLog()
            newl = Log(
                uid=16,
                t_hash="abc",
                o_hash="def",
                pdf="NNPDF",
                hash="16",
                log=pickle.dumps(working_log),
            )
            benchsession.add(newl)
            log = MyLog()
            log["_crash"] = [1, 2, 3]
            log["False"] = "This is going through"
            newl = Log(
                uid=17,
                t_hash="abc",
                o_hash="def",
                pdf="NNPDF",
                hash="17",
                log=pickle.dumps(log),
            )
            benchsession.add(newl)

        crash = benchnav.crashed_log(17)
        assert crash["_crash"] == "3 points"  # len([1, 2, 3])
        assert crash["False"] == "This is going through"

        with pytest.raises(ValueError, match="didn't crash"):
            benchnav.crashed_log(16)
