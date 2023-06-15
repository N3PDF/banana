import pathlib
import pickle

import pandas as pd
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
    def test_show_full_logs(self, benchsession, benchnav):
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

    def test_get_by_log(self, benchsession, benchnav):
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

    def test_as_dfd(self, benchsession, benchnav):
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

    def test_simlogs(self, benchsession, benchnav):
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

    def test_crashed(self, benchsession, benchnav):
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

    def test_subtract(self, benchsession, benchnav):
        with benchsession.begin():
            newt = Theory(uid=42, PTO=31, hash="abc")
            benchsession.add(newt)
            newo = OCard(uid=21, process=0, hash="def")
            benchsession.add(newo)

            def newl(uid, log, th="abc", oh="def", pdf="NNPDF"):
                return Log(
                    uid=uid,
                    t_hash=th,
                    o_hash=oh,
                    pdf=pdf,
                    hash=str(uid),
                    log=pickle.dumps(log),
                )

            dfd1 = dfdict.DFdict()
            dfd1["table1"] = pd.DataFrame(
                [
                    dict(x=0.1, Q2=10, my=100, my_error=1, percent_error=1, ext=99),
                    dict(x=0.2, Q2=10, my=100, my_error=1, percent_error=1, ext=100),
                    dict(x=0.3, Q2=10, my=100, my_error=1, percent_error=1, ext=100),
                ],
            )
            dfd1["table2"] = pd.DataFrame(
                [dict(x=0.1, Q2=10, my=100, my_error=1, percent_error=1, ext=99)]
            )
            dfd1["_ciao"] = pd.DataFrame(["Not in comparison"])
            dfd1["come"] = pd.DataFrame(["Not matching dfd2"])
            benchsession.add(newl(1, dfd1.to_document()))
            dfd2 = dfdict.DFdict()
            dfd2["table1"] = pd.DataFrame(
                [
                    dict(x=0.1, Q2=10, my=101, my_error=1, percent_error=1, ext=98),
                    dict(x=0.2, Q2=10, my=101, my_error=1, percent_error=1, ext=100),
                    dict(x=0.3, Q2=10, my=100, my_error=1, percent_error=1, ext=100),
                ],
            )
            dfd2["table2"] = pd.DataFrame(
                [dict(x=0.1, Q2=10, my=100, my_error=1, percent_error=1, ext1=99)]
            )
            benchsession.add(newl(2, dfd2.to_document()))
            dfd3 = dfdict.DFdict()
            dfd3["table2"] = pd.DataFrame(
                [dict(x=0.2, Q2=1e6, my=101, my_error=1, percent_error=1, ext=98)]
            )
            benchsession.add(newl(3, dfd3.to_document()))

        benchnav.myname = "my"
        diff = benchnav.subtract_tables(1, 2)
        assert "Subtracting" in diff.msgs[0]
        assert diff["table1"]["my"][0] == -1
        assert diff["table1"]["my_error"][0] == 2
        assert diff["table1"]["ext"][0] == 1

        with pytest.raises(ValueError, match="Cannot compare"):
            diff = benchnav.subtract_tables(1, 3)

    def test_compare_external(self, benchsession, benchnav):
        with benchsession.begin():
            newt = Theory(uid=42, PTO=31, hash="abc")
            benchsession.add(newt)
            newo = OCard(uid=21, process=0, hash="def")
            benchsession.add(newo)

            def newc(uid, res, ext, th="abc", oh="def", pdf="NNPDF"):
                return Cache(
                    uid=uid,
                    t_hash=th,
                    o_hash=oh,
                    pdf=pdf,
                    hash=str(uid),
                    result=pickle.dumps(res),
                    #  result=pickle.dumps({"table": [{"column": "value"}]}),
                    external=ext,
                )

            cache1 = dict(
                table=[
                    dict(x=0.1, Q2=10, result=99),
                    dict(x=0.2, Q2=10, result=100),
                    dict(x=0.3, Q2=10, result=0),
                ],
                ciao=["Not matching cache2"],
            )
            benchsession.add(newc(1, cache1, "blub"))
            cache2 = dict(
                table=[
                    dict(x=0.1, Q2=10, result=99),
                    dict(x=0.2, Q2=10, result=0),
                    dict(x=0.3, Q2=10, result=0),
                ],
                table2=[dict(x=0.1, Q2=10, result=99)],
            )
            benchsession.add(newc(2, cache2, "blab"))
            cache3 = cache2.copy()
            cache3["table2"] = [dict(x=1e-6, Q2=1e6, result=99)]
            benchsession.add(newc(3, cache3, "blub"))

        benchnav.myname = "my"
        diff = benchnav.compare_external(1, 2)
        assert "Comparing" in diff.msgs[0]
        assert diff["table"]["blub"][0] == 99
        assert diff["table"]["blab"][0] == 99
        assert diff["table"]["percent_error"][0] == 0.0

        diff = benchnav.compare_external(1, 3)
        assert "blub1" in diff["table"]
        assert "blub2" in diff["table"]

        with pytest.raises(ValueError, match="Cannot compare"):
            diff = benchnav.compare_external(2, 3)
