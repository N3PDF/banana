# -*- coding: utf-8 -*-
import copy

import numpy as np
import pytest
from utils import cd, lhapdf_path, test_pdf

from banana import toy
from banana.data import genpdf

# try:
#     import lhapdf
# except ImportError:
#     pytest.skip("No LHAPDF interface around", allow_module_level=True)
# TODO mark file skipped in coverage.py
lhapdf = pytest.importorskip("lhapdf")


def test_is_evolution():
    assert genpdf.is_evolution_labels(["V", "T3"])
    assert not genpdf.is_evolution_labels(["21", "2"])


def test_is_pids():
    assert not genpdf.is_pid_labels(["V", "T3"])
    assert not genpdf.is_pid_labels(["35", "9"])
    assert not genpdf.is_pid_labels({})
    assert genpdf.is_pid_labels([21, 2])


def test_genpdf_exceptions(tmp_path):
    # using a wrong label and then a wrong parent pdf
    with cd(tmp_path):
        with pytest.raises(ValueError):
            genpdf.generate_pdf(
                "debug",
                ["f"],
                {21: lambda x, Q2: 3 * x * (1 - x), 2: lambda x, Q2: 4 * x * (1 - x)},
            )
        with pytest.raises(ValueError):
            genpdf.generate_pdf(
                "debug",
                ["g"],
                10,
            )
        with pytest.raises(FileExistsError):
            genpdf.install_pdf("foo")

        with pytest.raises(TypeError):
            genpdf.generate_pdf("debug", [21], info_update=(10, 15, 20))


def test_genpdf_no_parent_and_install(tmp_path):
    with cd(tmp_path):
        d = tmp_path / "sub"
        d.mkdir()
        with lhapdf_path(d):
            genpdf.generate_pdf("debug", [21], install=True)
        with lhapdf_path(d):
            pdf = lhapdf.mkPDF("debug", 0)
            for x in [0.1, 0.2, 0.8]:
                for Q2 in [10, 20, 100]:
                    np.testing.assert_allclose(
                        pdf.xfxQ2(21, x, Q2), x * (1 - x), rtol=3e-5
                    )
                    np.testing.assert_allclose(pdf.xfxQ2(2, x, Q2), 0.0)


def test_genpdf_toy(tmp_path):
    with cd(tmp_path):
        toylh = toy.mkPDF("", 0)
        genpdf.generate_pdf(
            "debug", [21], "toy", info_update={"NumFlavors": 25, "Debug": "Working"}
        )
        with lhapdf_path(tmp_path):
            # testing info updating
            info = genpdf.load.load_info_from_file("debug")
            assert info["NumFlavors"] == 25
            assert info["Debug"] == "Working"

            pdf = lhapdf.mkPDF("debug", 0)
            for x in [0.1, 0.2, 0.5]:
                for Q2 in [10, 20, 100]:
                    np.testing.assert_allclose(
                        pdf.xfxQ2(21, x, Q2), toylh.xfxQ2(21, x, Q2), rtol=3e-5
                    )
                    np.testing.assert_allclose(pdf.xfxQ2(2, x, Q2), 0.0)


def test_genpdf_parent_evolution_basis(tmp_path):
    with cd(tmp_path):
        with lhapdf_path(test_pdf):
            CT14 = lhapdf.mkPDF("myCT14llo_NF3", 0)
            genpdf.generate_pdf("debug2", ["g"], "myCT14llo_NF3")
        with lhapdf_path(tmp_path):
            pdf = lhapdf.mkPDF("debug2", 0)
            for x in [0.1, 0.2, 0.5]:
                for Q2 in [10, 20, 100]:
                    np.testing.assert_allclose(
                        pdf.xfxQ2(21, x, Q2), CT14.xfxQ2(21, x, Q2), rtol=3e-5
                    )
                    np.testing.assert_allclose(pdf.xfxQ2(2, x, Q2), 0.0)


def test_genpdf_dict(tmp_path):
    with cd(tmp_path):
        genpdf.generate_pdf(
            "debug",
            [21],
            {21: lambda x, Q2: 3 * x * (1 - x), 2: lambda x, Q2: 4 * x * (1 - x)},
        )
        with lhapdf_path(tmp_path):
            pdf = lhapdf.mkPDF("debug", 0)
            for x in [0.1, 0.2, 0.8]:
                for Q2 in [10, 20, 100]:
                    np.testing.assert_allclose(
                        pdf.xfxQ2(21, x, Q2), 3 * x * (1 - x), rtol=3e-5
                    )
                    np.testing.assert_allclose(pdf.xfxQ2(2, x, Q2), 0.0)


def test_genpdf_MSTW_allflavors(tmp_path):
    with cd(tmp_path):
        MSTW = lhapdf.mkPDF("MSTW2008nnlo90cl_nf4as5", 0)
        # filtering on all flavors
        genpdf.generate_pdf(
            "My_MSTW",
            [21, 1, 2, 3, 4, 5, 6, -1, -2, -3, -4, -5, -6],
            "MSTW2008nnlo90cl_nf4as5",
        )
    with lhapdf_path(tmp_path):
        pdf = lhapdf.mkPDF("My_MSTW", 0)
        # testing for some pids, x and Q2 values
        for x in [0.1, 0.2, 0.8]:
            for Q2 in [10, 20, 100]:
                for pid in [21, 1, 4, 6, -2, -3, -5]:
                    np.testing.assert_allclose(
                        pdf.xfxQ2(pid, x, Q2), MSTW.xfxQ2(pid, x, Q2), rtol=3e-8
                    )
