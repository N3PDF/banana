# -*- coding: utf-8 -*-
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
    pass
    #  def test_t(self, banana_cfg):
    #  app = FakeNavApp(banana_cfg, "test")
    #  df = app.list_all("t")
    #  assert len(df) == 0
    #  dt = datetime.datetime.now().isoformat()
    #  write_input(banana_cfg, {"theories": {1: {"PTO": 0, "_created": dt}}})
    #  df = app.list_all("t")
    #  assert len(df) == 1
    #  r = df.to_dict(orient="records")
    #  assert r[0]["PTO"] == 0
    #  assert r[0]["created"] == "just now"
    #  r0 = app.get("t", 1)
    #  assert r0.doc_id == 1
    #  assert r0["PTO"] == 0
    #  assert r0["_created"] == dt

    def test_l(self, banana_yaml, dbsession, tab_ciao):
        tabman = tm.TableManager(dbsession, tab_ciao)
        app = FakeNavApp(dbsession, banana_yaml, "test", extra_tables=dict(ciao=tabman))

        df = app.list_all("ciao")
        assert len(df) == 0

        with dbsession.begin():
            newrec = tab_ciao(uid=42, name="leorio", hash="abcdef123456789")
            dbsession.add(newrec)
        df = app.list_all("ciao")
        assert len(df) == 1

    #  def test_tn(self, banana_cfg):
    #  app = FakeNavApp(banana_cfg, "test")
    #  with pytest.raises(ValueError):
    #  app.list_all("b")

    #  def test_cm(self, banana_cfg):
    #  app = FakeNavApp(banana_cfg, "test")
    #  # identity
    #  app.change_mode("test")
    #  # non-exsistent mode
    #  with pytest.raises(KeyError):
    #  app.change_mode("bla")
