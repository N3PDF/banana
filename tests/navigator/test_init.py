from banana import navigator


class FakeApp(navigator.navigator.NavigatorApp):
    def is_valid_physical_object(_name):
        return True


def test_register(banana_yaml):
    mod = {}
    navigator.register_globals(mod, FakeApp(banana_yaml, "test"))
    for n in ["t", "ls", "g", "logs", "dfl", "diff", "simlogs"]:
        assert n in mod


def test_launch(monkeypatch, capsys, banana_yaml):
    # mock ipython launch
    monkeypatch.setattr("IPython.start_ipython", lambda **kwargs: print(kwargs))

    # attempt to launch with fake modules
    navigator.launch_navigator(["test", "testmark"], skip_cfg=True)
    captured = capsys.readouterr()
    assert "--pylab" in captured.out
    assert "test" in captured.out
    assert "testmark" in captured.out
    assert len(eval(captured.out)["argv"]) == 3

    # attempt to launch with no modules
    navigator.launch_navigator([], skip_cfg=True)
    captured1 = capsys.readouterr()
    assert eval(captured1.out)["argv"] == ["--pylab"]
    navigator.launch_navigator(skip_cfg=True)
    captured2 = capsys.readouterr()
    assert captured1 == captured2

    # attempt to launch with no pylab
    navigator.launch_navigator([], skip_cfg=True, pylab=False)
    captured = capsys.readouterr()
    assert "--pylab" not in captured.out

    # attempt to launch with config detection
    navigator.launch_navigator([])
