# -*- coding: utf-8 -*-
import pathlib

import pytest
import numpy as np

from banana import navigator


class FakeApp(navigator.NavigatorApp):
    def is_valid_physical_object(name):
        return True


@pytest.fixture
def banana_cfg(fs):
    fs.create_file("/tmp/input.json")
    fs.create_file("/tmp/output.json")
    cfg = {
        "database_path": f"/tmp/benchmark-{int(np.random.rand() * 1e6)}.db",
        "input_tables": ["theories", "cache"],
    }
    return cfg


def test_register(banana_cfg):
    mod = {}
    navigator.register_globals(mod, FakeApp(banana_cfg, "test"))
    for n in ["t", "ls", "g"]:
        assert n in mod


def test_launch(monkeypatch, capsys):
    monkeypatch.setattr("IPython.start_ipython", lambda **kwargs: print(kwargs))
    navigator.launch_navigator("test", "testmark")
    captured = capsys.readouterr()
    assert "--pylab" in captured.out
