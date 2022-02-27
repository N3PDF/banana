# -*- coding: utf-8 -*-
import pytest

from banana.navigator import table_manager as tm


class TestTableManager:
    def test_init(self):
        session = "mysession"
        table_object = "mytable"
        tabman = tm.TableManager(session, table_object)
        assert tabman.session == session
        assert tabman.table_object == table_object
