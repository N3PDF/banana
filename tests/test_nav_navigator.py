# -*- coding: utf-8 -*-
import pathlib
import datetime

import json
import pytest

from banana import navigator

class FakeNavApp(navigator.NavigatorApp):
    def fill_theories(self, theo, obj):
        obj["PTO"] = theo["PTO"]

def read_input(cur_banana_cfg):
    with open(
        cur_banana_cfg["dir"]
        / cur_banana_cfg["data_dir"]
        / cur_banana_cfg["modes"]["test"]["input_db"],
        "r",
    ) as o:
        inp = json.load(o)
    return inp

def write_input(cur_banana_cfg, cnt):
    with open(
        cur_banana_cfg["dir"]
        / cur_banana_cfg["data_dir"]
        / cur_banana_cfg["modes"]["test"]["input_db"],
        "w",
    ) as o:
        json.dump(cnt,o)

@pytest.fixture
def banana_cfg(fs):
    fs.create_file('/tmp/input.json')
    fs.create_file('/tmp/output.json')
    cfg = {
        "dir": pathlib.Path("/tmp/"),
        "data_dir": ".",
        "input_tables": ["theories", "otest"],
        "modes": {"test": {"input_db": "input.json", "theories": {"PTO": [0]}}},
    }
    return cfg

class TestNavigatorApp():
    def test_t(self, banana_cfg):
        app = FakeNavApp(banana_cfg, "test")
        df = app.list_all("t")
        assert len(df) == 0
        dt = datetime.datetime.now().isoformat()
        write_input(banana_cfg,{"theories": {1: {"PTO": 0, "_created": dt}}})
        df = app.list_all("t")
        assert len(df) == 1
        r = df.to_dict(orient="records")
        assert r[0]["PTO"] == 0
        assert r[0]["created"] == "just now"
        r0 = app.get("t", 1)
        assert r0.doc_id == 1
        assert r0["PTO"] == 0
        assert r0["_created"] == dt

    def test_l(self, banana_cfg):
        app = FakeNavApp(banana_cfg, "test")
        df = app.list_all("l")
        assert len(df) == 0

    def test_tn(self, banana_cfg):
        app = FakeNavApp(banana_cfg, "test")
        with pytest.raises(ValueError):
            app.list_all("b")

    def test_cm(self, banana_cfg):
        app = FakeNavApp(banana_cfg, "test")
        # identity
        app.change_mode("test")
        # non-exsistent mode
        with pytest.raises(KeyError):
            app.change_mode("bla")
