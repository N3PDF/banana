# -*- coding: utf-8 -*-
import numpy as np
import pytest
from utils import cd, lhapdf_path, test_pdf

from banana.data import genpdf

lhapdf = pytest.importorskip("lhapdf")


def test_filter_pids_raw():
    blocks = [
        {
            "Q2grid": np.array([1, 2]),
            "xgrid": np.array([0.1, 1.0]),
            "pids": np.array([-1, 21, 1]),
            "data": np.array([[0.1, 0.2, 0.3]] * 4),
        }
    ]
    gonly = genpdf.filter.filter_pids(blocks, [21])
    assert len(gonly) == 1
    np.testing.assert_allclose(gonly[0]["data"], np.array([[0.0, 0.2, 0.0]] * 4))
    gdonly = genpdf.filter.filter_pids(blocks, [21, 1])
    assert len(gdonly) == 1
    np.testing.assert_allclose(gdonly[0]["data"], np.array([[0.0, 0.2, 0.3]] * 4))
    uonly = genpdf.filter.filter_pids(blocks, [2])
    assert len(uonly) == 1
    np.testing.assert_allclose(uonly[0]["data"], np.array([[0.0, 0.0, 0.0]] * 4))


def test_filter_pids_ct14(tmp_path):
    with cd(tmp_path):
        # read the debug PDFs
        with lhapdf_path(test_pdf):
            info = genpdf.load.load_info_from_file("myCT14llo_NF3")
            blocks = genpdf.load.load_blocks_from_file("myCT14llo_NF3", 0)
            pdf = lhapdf.mkPDF("myCT14llo_NF3", 0)
        # now extract the gluon
        new_blocks = genpdf.filter.filter_pids(blocks, [21])
        genpdf.export.dump_set("gonly", info, [new_blocks])
        with lhapdf_path(tmp_path):
            gonly = lhapdf.mkPDF("gonly", 0)
            # all quarks are 0
            for pid in [1, 2, -3]:
                for x in [1e-2, 0.1, 0.9]:
                    for Q2 in [10, 100]:
                        np.testing.assert_allclose(gonly.xfxQ2(pid, x, Q2), 0.0)
            # and the gluon in as before
            for x in [1e-2, 0.1, 0.9]:
                for Q2 in [10, 100]:
                    np.testing.assert_allclose(
                        pdf.xfxQ2(21, x, Q2), gonly.xfxQ2(21, x, Q2)
                    )


def test_filter_evol_ct14(tmp_path):
    with cd(tmp_path):
        # read the debug PDFs
        with lhapdf_path(test_pdf):
            info = genpdf.load.load_info_from_file("myCT14llo_NF3")
            blocks = genpdf.load.load_blocks_from_file("myCT14llo_NF3", 0)
            pdf = lhapdf.mkPDF("myCT14llo_NF3", 0)
        # now extract the gluon
        new_blocks = genpdf.filter.filter_evol(blocks, ["g"])
        info["Flavors"] = [22, -6, -5, -4, -3, -2, -1, 21, 1, 2, 3, 4, 5, 6]
        genpdf.export.dump_set("gonly2", info, [new_blocks])
        with lhapdf_path(tmp_path):
            gonly = lhapdf.mkPDF("gonly2", 0)
            # all quarks are 0
            for pid in [1, 2, -3]:
                for x in [1e-2, 0.1, 0.9]:
                    for Q2 in [10, 100]:
                        np.testing.assert_allclose(gonly.xfxQ2(pid, x, Q2), 0.0)
            # and the gluon in as before
            for x in [1e-2, 0.1, 0.9]:
                for Q2 in [10, 100]:
                    np.testing.assert_allclose(
                        pdf.xfxQ2(21, x, Q2), gonly.xfxQ2(21, x, Q2)
                    )


def test_filter_evol_raw():
    blocks = [
        {
            "Q2grid": np.array([1, 2]),
            "xgrid": np.array([0.1, 1.0]),
            "pids": np.array([-1, 21, 1]),
            "data": np.array([[0.1, 0.2, 0.1]] * 4),
        }
    ]
    gonly = genpdf.filter.filter_evol(blocks, ["g"])
    assert len(gonly) == 1
    np.testing.assert_allclose(
        gonly[0]["data"],
        np.array(
            [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]] * 4
        ),
    )
    Sonly = genpdf.filter.filter_evol(blocks, ["S"])
    assert len(Sonly) == 1
    for i in [0, 1, 2, 3]:
        # g and gamma are zero
        np.testing.assert_allclose(Sonly[0]["data"][i][7], 0)
        np.testing.assert_allclose(Sonly[0]["data"][i][0], 0)
        # quark are all equal and equal to anti-quarks
        for pid in [2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13]:
            np.testing.assert_allclose(Sonly[0]["data"][i][pid], Sonly[0]["data"][i][1])


def test_filter_evol_nodata():
    # try with a block without data
    blocks = [
        {
            "Q2grid": np.array([1, 2]),
            "xgrid": np.array([0.1, 1.0]),
            "pids": np.array([-1, 21, 1]),
            "data": np.array([]),
        },
        {
            "Q2grid": np.array([1, 2]),
            "xgrid": np.array([0.1, 1.0]),
            "pids": np.array([-1, 21, 1]),
            "data": np.array([[0.1, 0.2, 0.1]] * 4),
        },
    ]
    gonly = genpdf.filter.filter_evol(blocks, ["g"])
    assert len(gonly) == 2
    np.testing.assert_allclose(
        gonly[1]["data"],
        np.array(
            [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]] * 4
        ),
    )
