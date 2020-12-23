# -*- coding: utf-8 -*-
import pathlib

import pytest

from banana import navigator

class FakeApp(navigator.NavigatorApp):
    pass

@pytest.fixture
def banana_cfg(fs):
    fs.create_file('/tmp/input.json')
    fs.create_file('/tmp/output.json')
    cfg = {
        "dir": pathlib.Path("/tmp/"),
        "data_dir": ".",
        "input_tables": ["theories", "otest"],
        "modes": {"test": {"input_db": "input.json", "theories": {"PTO": [0, 1]}}},
    }
    return cfg

def test_register(banana_cfg):
    mod = {}
    navigator.register_globals(mod, FakeApp(banana_cfg,"test"))
    for n in ["t", "ls", "g"]:
        assert n in mod

def test_launch(monkeypatch,capsys):
    monkeypatch.setattr("IPython.start_ipython", lambda **kwargs: print(kwargs))
    navigator.launch_navigator("test", "testmark")
    captured = capsys.readouterr()
    assert "--pylab" in captured.out
