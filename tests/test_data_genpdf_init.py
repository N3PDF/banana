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
    labels = ["V", "T3"]
    assert genpdf.is_evolution_labels(labels) == True
    labels2 = ["21", "2"]
    assert genpdf.is_evolution_labels(labels2) == False


def test_is_pids():
    labels = ["V", "T3"]
    assert genpdf.is_pid_labels(labels) == False
    labels2 = [21, 2]
    assert genpdf.is_pid_labels(labels2) == True


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
        genpdf.generate_pdf("debug", [21], "toy")
        with lhapdf_path(tmp_path):
            pdf = lhapdf.mkPDF("debug", 0)
            for x in [0.1, 0.2, 0.5]:
                for Q2 in [10, 20, 100]:
                    np.testing.assert_allclose(
                        pdf.xfxQ2(21, x, Q2), toylh.xfxQ2(21, x, Q2), rtol=3e-5
                    )
                    np.testing.assert_allclose(pdf.xfxQ2(2, x, Q2), 0.0)


# TODO: fix the problem of flavour metadata (affecting also filter testing)
# def test_genpdf_parent_evolution_basis(tmp_path):
#     with cd(tmp_path):
#         with lhapdf_path(test_pdf):
#             CT14 = lhapdf.mkPDF("myCT14llo_NF3", 0)

#         genpdf.generate_pdf(
#             "debug",
#             ["g"],
#             "myCT14llo_NF3"
#         )
#         with lhapdf_path(tmp_path):
#             pdf = lhapdf.mkPDF("debug", 0)
#             for x in [0.1, 0.2, 0.5]:
#                 for Q2 in [10, 20, 100]:
#                     np.testing.assert_allclose(
#                         pdf.xfxQ2(21, x, Q2), CT14.xfxQ2(21, x, Q2), rtol=3e-5
#                     )
#                     np.testing.assert_allclose(pdf.xfxQ2(2, x, Q2), 0.0)


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
