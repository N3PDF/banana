# -*- coding: utf-8 -*-
import os
import pathlib
from contextlib import contextmanager

import numpy as np
import pytest

from banana.data import generate_pdf2

# try:
#     import lhapdf
# except ImportError:
#     pytest.skip("No LHAPDF interface around", allow_module_level=True)
# TODO mark file skipped in coverage.py
lhapdf = pytest.importorskip("lhapdf")

test_pdf = pathlib.Path(__file__).parent / "generate_pdf"

# thanks https://stackoverflow.com/questions/431684/how-do-i-change-the-working-directory-in-python/24176022#24176022
@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)


# lets follow the same spirit
@contextmanager
def lhapdf_path(newdir):
    path = lhapdf.paths()
    lhapdf.pathsPrepend(str(newdir))
    try:
        yield
    finally:
        lhapdf.setPaths(path)


def test_load_data_ct14():
    with lhapdf_path(test_pdf):
        blocks = generate_pdf2.load.load_blocks_from_file("myCT14llo_NF3", 0)
        assert len(blocks) == 1
        b0 = blocks[0]
        assert isinstance(b0, dict)
        assert sorted(b0.keys()) == sorted(["pids", "xgrid", "Q2grid", "data"])
        assert sorted(b0["pids"]) == sorted([-3, -2, -1, 21, 1, 2, 3])
        np.testing.assert_allclose(b0["xgrid"][0], 1e-9)


def test_load_data_mstw():
    with lhapdf_path(test_pdf):
        blocks = generate_pdf2.load.load_blocks_from_file("myMSTW2008nlo90cl", 0)
        assert len(blocks) == 3
        b0 = blocks[0]
        assert isinstance(b0, dict)
        assert sorted(b0.keys()) == sorted(["pids", "xgrid", "Q2grid", "data"])
        assert sorted(b0["pids"]) == sorted([-5, -4, -3, -2, -1, 21, 1, 2, 3, 4, 5])
        np.testing.assert_allclose(b0["xgrid"][0], 1e-6)


def test_load_info():
    with lhapdf_path(test_pdf):
        info = generate_pdf2.load.load_info_from_file("myCT14llo_NF3")
        assert "SetDesc" in info
        assert "fake" in info["SetDesc"]
        assert sorted(info["Flavors"]) == sorted([-3, -2, -1, 21, 1, 2, 3])
