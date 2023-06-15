import builtins
import datetime

import pytest

from banana.navigator import table_manager as tm


def make_asserter(session, tab, fn):
    def asserter(value, eq=True):
        with session.begin():
            available = session.query(tab).all()
            if eq:
                assert fn(available) == value
            else:
                assert fn(available) != value

    return asserter


class TestTableManager:
    def test_init(self):
        session = "mysession"
        table = "mytable"
        tabman = tm.TableManager(session, table)
        assert tabman.session == session
        assert tabman.table_object == table

    def test_remove(self, dbsession, tab_ciao):
        tabman = tm.TableManager(dbsession, tab_ciao)
        assert_len = make_asserter(dbsession, tab_ciao, builtins.len)

        assert_len(0)

        for doc_id in (42, "abc", -1, dict(uid=42)):
            with dbsession.begin():
                newrec = tab_ciao(uid=42, name="leorio", hash="abcdef123456789")
                dbsession.add(newrec)
            assert_len(1)

            tabman.remove([doc_id])
            assert_len(0)

        with pytest.raises(ValueError, match="can not .* identify"):
            tabman.remove([()])

    def test_truncate(self, dbsession, tab_ciao, monkeypatch):
        tabman = tm.TableManager(dbsession, tab_ciao)
        assert_len = make_asserter(dbsession, tab_ciao, builtins.len)

        assert_len(0)

        with dbsession.begin():
            newrecs = [
                tab_ciao(uid=uid, name="leorio", hash="abcdef123456789")
                for uid in range(10)
            ]
            dbsession.add_all(newrecs)
        assert_len(10)

        monkeypatch.setattr("builtins.input", lambda _: "n")
        tabman.truncate()
        assert_len(10)

        monkeypatch.setattr("builtins.input", lambda _: "y")
        tabman.truncate()
        assert_len(0)

    def test_update_atime(self, dbsession, tab_ciao):
        tabman = tm.TableManager(dbsession, tab_ciao)
        assert_atime = make_asserter(dbsession, tab_ciao, lambda a: a[0].atime)

        millennium = datetime.datetime(2000, 1, 1, 00, 00, 00)
        with dbsession.begin():
            newrec = tab_ciao(
                uid=42, name="leorio", hash="abcdef123456789", atime=millennium
            )
            dbsession.add(newrec)

        assert_atime(millennium)

        tabman.update_atime([dict(uid=42)])
        assert_atime(millennium, eq=False)

    def test_all(self, dbsession, tab_ciao):
        tabman = tm.TableManager(dbsession, tab_ciao)
        assert_len = make_asserter(dbsession, tab_ciao, builtins.len)
        assert_atime = make_asserter(dbsession, tab_ciao, lambda a: a[0].atime)

        assert_len(0)

        millennium = datetime.datetime(2000, 1, 1, 00, 00, 00)
        with dbsession.begin():
            newrecs = [
                tab_ciao(
                    uid=uid, name="leorio", hash="abcdef123456789", atime=millennium
                )
                for uid in range(10)
            ]
            dbsession.add_all(newrecs)
        assert_len(10)
        assert_atime(millennium)

        recs = tabman.all()
        assert len(recs) == 10
        for i in range(10):
            assert recs[i] != millennium

    def test_get(self, dbsession, tab_ciao):
        tabman = tm.TableManager(dbsession, tab_ciao)
        assert_len = make_asserter(dbsession, tab_ciao, builtins.len)
        assert_atime = make_asserter(dbsession, tab_ciao, lambda a: a[0].atime)

        assert_len(0)

        millennium = datetime.datetime(2000, 1, 1, 00, 00, 00)
        with dbsession.begin():
            newrec = tab_ciao(
                uid=42, name="leorio", hash="abcdef123456789", atime=millennium
            )
            dbsession.add(newrec)
        assert_len(1)

        for doc_id in (42, "abc", -1):
            assert_len(1)

            rec = tabman.get(doc_id)
            assert rec["name"] == "leorio"
            assert_atime(millennium, eq=False)

        with pytest.raises(
            ValueError, match="key passed .* not correspond .* partial hash.* uid"
        ):
            tabman.get([])
