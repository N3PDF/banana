# -*- coding: utf-8 -*-
import pytest

from banana.navigator import table_manager as tm


def make_len_asserter(session, tab):
    def assert_len(length):
        with session.begin():
            available = session.query(tab).all()
            assert len(available) == length

    return assert_len


class TestTableManager:
    def test_init(self):
        session = "mysession"
        table = "mytable"
        tabman = tm.TableManager(session, table)
        assert tabman.session == session
        assert tabman.table_object == table

    def test_remove(self, dbsession, tab_ciao):
        tabman = tm.TableManager(dbsession, tab_ciao)
        assert_len = make_len_asserter(dbsession, tab_ciao)

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
        assert_len = make_len_asserter(dbsession, tab_ciao)

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
