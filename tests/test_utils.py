import pytest

from banana import utils

lhapdf = pytest.importorskip("lhapdf")


def test_lhapdf_path(tmp_path):
    assert str(tmp_path) not in lhapdf.paths()
    with utils.lhapdf_path(tmp_path):
        assert str(tmp_path) in lhapdf.paths()
    assert str(tmp_path) not in lhapdf.paths()
