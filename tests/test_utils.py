# -*- coding: utf-8 -*-
from banana import utils


def test_lhapdf_path(tmp_path, lhapdf):
    assert str(tmp_path) not in lhapdf.paths()

    with utils.lhapdf_path(tmp_path):
        assert str(tmp_path) in lhapdf.paths()

    assert str(tmp_path) not in lhapdf.paths()
