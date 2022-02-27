# -*- coding: utf-8 -*-
from banana.navigator import table_manager as tm


class TestTableManager:
    def test_init(self):
        session = "mysession"
        table = "mytable"
        tabman = tm.TableManager(session, table)
        assert tabman.session == session
        assert tabman.table_object == table

    def test_remove(self, dbsession, tab_ciao):
        tabman = tm.TableManager(dbsession, tab_ciao)

        def assert_len(length):
            with dbsession.begin():
                available = dbsession.query(tab_ciao).all()
                assert len(available) == length

        assert_len(0)

        with dbsession.begin():
            newrec = tab_ciao(uid=42, name="leorio")
            dbsession.add(newrec)
        assert_len(1)

        tabman.remove([42])
        assert_len(0)
