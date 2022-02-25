# -*- coding: utf-8 -*-
from banana import navigator


class FakeApp(navigator.navigator.NavigatorApp):
    def is_valid_physical_object(_name):
        return True


def test_register(banana_yaml):
    mod = {}
    navigator.register_globals(mod, FakeApp(banana_yaml, "test"))
    for n in ["t", "ls", "g", "logs", "dfl", "diff", "simlogs"]:
        assert n in mod


def test_launch(monkeypatch, capsys):
    monkeypatch.setattr("IPython.start_ipython", lambda **kwargs: print(kwargs))
    navigator.launch_navigator(["test", "testmark"], skip_cfg=True)
    captured = capsys.readouterr()
    assert "--pylab" in captured.out
