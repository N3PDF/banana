# -*- coding: utf-8 -*-
import pytest

from banana import navigator
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

    #  def test_cm(self, banana_cfg):
    #  app = FakeNavApp(banana_cfg, "test")
    #  # identity
    #  app.change_mode("test")
    #  # non-exsistent mode
    #  with pytest.raises(KeyError):
    #  app.change_mode("bla")
