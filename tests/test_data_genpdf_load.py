# -*- coding: utf-8 -*-

import numpy as np
import pytest
from utils import lhapdf_path, test_pdf

from banana.data import genpdf

# try:
#     import lhapdf
# except ImportError:
#     pytest.skip("No LHAPDF interface around", allow_module_level=True)
# TODO mark file skipped in coverage.py
lhapdf = pytest.importorskip("lhapdf")


def test_load_data_ct14():
    with lhapdf_path(test_pdf):
        blocks = genpdf.load.load_blocks_from_file("myCT14llo_NF3", 0)
        assert len(blocks) == 1
        b0 = blocks[0]
        assert isinstance(b0, dict)
        assert sorted(b0.keys()) == sorted(["pids", "xgrid", "Q2grid", "data"])
        assert sorted(b0["pids"]) == sorted([-3, -2, -1, 21, 1, 2, 3])
        assert len(b0["data"].T) == 7
        np.testing.assert_allclose(b0["xgrid"][0], 1e-9)


def test_load_data_mstw():
    with lhapdf_path(test_pdf):
        blocks = genpdf.load.load_blocks_from_file("myMSTW2008nlo90cl", 0)
        assert len(blocks) == 3
        b0 = blocks[0]
        assert isinstance(b0, dict)
        assert sorted(b0.keys()) == sorted(["pids", "xgrid", "Q2grid", "data"])
        assert sorted(b0["pids"]) == sorted([-5, -4, -3, -2, -1, 21, 1, 2, 3, 4, 5])
        np.testing.assert_allclose(b0["xgrid"][0], 1e-6)


def test_load_info():
    with lhapdf_path(test_pdf):
        info = genpdf.load.load_info_from_file("myCT14llo_NF3")
        assert "SetDesc" in info
        assert "fake" in info["SetDesc"]
        assert sorted(info["Flavors"]) == sorted([-3, -2, -1, 21, 1, 2, 3])
