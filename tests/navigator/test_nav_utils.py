from banana.navigator import utils


def test_comparison(capsys):
    a = dict(c=1, d=2, _e=3)
    b = dict(c=1, d=3, _e=4)
    utils.compare_dicts(a, b, exclude_underscored=True)
    captured = capsys.readouterr()
    assert captured.err == ""
    assert "c" not in captured.out
    assert "d" in captured.out
    assert "_e" not in captured.out


def test_comparison_underscore(capsys):
    a = dict(c=1, d=2, _e=3, f=4)
    b = dict(c=1, d=3, _e=4, g=5)
    utils.compare_dicts(a, b)
    captured = capsys.readouterr()
    assert captured.err == ""
    assert "c" not in captured.out
    assert "d" in captured.out
    assert "_e" in captured.out
    assert "f" in captured.out
    assert "g" in captured.out


def test_comparison_exclusion(capsys):
    a = dict(c=1, d=2, e=3)
    b = dict(c=1, d=3, e=4)
    utils.compare_dicts(a, b, exclude_keys=["e"])
    captured = capsys.readouterr()
    assert captured.err == ""
    assert "c" not in captured.out
    assert "d" in captured.out
    assert "e" not in captured.out
