# -*- coding: utf-8 -*-
import pytest

from banana.navigator import table_manager as t_m

class FakeTable:
    def __init__(self, name, data):
        self.name = name
        self.data = data
    def get(self, doc_id):
        return self.data[doc_id]
    def all(self):
        return self.data
    def truncate(self):
        self.data = {}

class TestTableManager:
    def test_get_all(self):
        d = {1: {"a":1}, 2: {"a": 2}}
        tm = t_m.TableManager(FakeTable("test", d))
        assert tm.all() == d
        assert tm.get(1) == d[1]

    def test_truncate(self, monkeypatch):
        d = {1: {"a":1}, 2: {"a": 2}}
        tm = t_m.TableManager(FakeTable("test", d))
        with pytest.raises(RuntimeError):
            tm.truncate()

        logs = t_m.TableManager(FakeTable("logs", d))
        monkeypatch.setattr("builtins.input", lambda _: "n")
        logs.truncate()
        assert logs.all() == d

    def test_truncate_yes(self, monkeypatch):
        d = {1: {"a":1}, 2: {"a": 2}}
        logs = t_m.TableManager(FakeTable("logs", d))
        monkeypatch.setattr("builtins.input", lambda _: "y")
        logs.truncate()
        assert logs.all() == {}
