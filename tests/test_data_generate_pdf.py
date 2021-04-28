# -*- coding: utf-8 -*-
from contextlib import contextmanager
import os
import subprocess
from unittest import mock

import numpy as np
import pytest

from banana.data import generate_pdf
from banana import toy

# try:
#    import lhapdf
# except ImportError:
#    pytest.skip("No LHAPDF interface around", allow_module_level=True)
# TODO mark file skipped in coverage.py
lhapdf = pytest.importorskip("lhapdf")

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


def test_generate_pdf_debug(tmp_path):
    pass
    #  with cd(tmp_path):
    #  install_path = tmp_path / "datadir"
    #  install_path.mkdir()
    #  with lhapdf_path(install_path):
    #  with mock.patch("sys.argv", ["", "test-d-bbar-only", "1", "-5", "-i"]):
    #  generate_pdf.generate_pdf()
    #  pdf = lhapdf.mkPDF("test-d-bbar-only", 0)
    #  for x in [0.1, 0.2]:
    #  np.testing.assert_allclose(pdf.xfxQ2(21, x, 1), 0.0)
    #  np.testing.assert_allclose(pdf.xfxQ2(5, x, 10), 0.0)
    #  # we have to use large Q2
    #  # - otherwise lhapdf will crash us (and even there it is ...)
    #  np.testing.assert_allclose(
    #  pdf.xfxQ2(1, x, 1000), x * (1.0 - x), rtol=1e-5
    #  )
    #  np.testing.assert_allclose(
    #  pdf.xfxQ2(-5, x, 1000), x * (1.0 - x), rtol=1e-5
    #  )


def test_generate_pdf_toy(tmp_path):
    pass
    #  with cd(tmp_path):
    #  install_path = tmp_path / "datadir"
    #  install_path.mkdir()
    #  with lhapdf_path(install_path):
    #  with mock.patch("sys.argv", ["", "test-toy-u-only", "-p", "toyLH", "2"]):
    #  generate_pdf.generate_pdf()
    #  with mock.patch("sys.argv", ["", "test-toy-u-only"]):
    #  generate_pdf.install_pdf()
    #  pdf = lhapdf.mkPDF("test-toy-u-only", 0)
    #  ref = toy.mkPDF("", 0)
    #  for x in [0.1, 0.2]:
    #  np.testing.assert_allclose(pdf.xfxQ2(21, x, 1), 0.0)
    #  np.testing.assert_allclose(pdf.xfxQ2(5, x, 10), 0.0)
    #  # we have to use large Q2
    #  # - otherwise lhapdf will crash us (and even there it is ...)
    #  np.testing.assert_allclose(
    #  pdf.xfxQ2(2, x, 1000), ref.xfxQ2(2, x, 1000), rtol=1e-5
    #  )
    #  with pytest.raises(FileExistsError):
    #  with mock.patch("sys.argv", ["", "test-toy-u-only"]):
    #  generate_pdf.install_pdf()


def test_generate_pdf_parent(tmp_path):
    pass
    #  with cd(tmp_path):
    #  with lhapdf_path(tmp_path):
    #  #  subprocess.run("lhapdf install NNPDF31_nlo_as_0118".split())
    #  lhapdf.getPDFSet("NNPDF31_nlo_as_0118")
    #  with mock.patch(
    #  "sys.argv", ["", "test-NNPDF-g-only", "-p", "NNPDF31_nlo_as_0118", "21"]
    #  ):
    #  generate_pdf.generate_pdf()
    #  with lhapdf_path(tmp_path):
    #  pdf = lhapdf.mkPDF("test-NNPDF-g-only", 0)
    #  ref = lhapdf.mkPDF("NNPDF31_nlo_as_0118", 0)
    #  for x in [0.1, 0.2]:
    #  np.testing.assert_allclose(pdf.xfxQ2(1, x, 1), 0.0)
    #  np.testing.assert_allclose(pdf.xfxQ2(5, x, 10), 0.0)
    #  # we have to use large Q2
    #  # - otherwise lhapdf will crash us (and even there it is ...)
    #  np.testing.assert_allclose(
    #  pdf.xfxQ2(21, x, 1000), ref.xfxQ2(21, x, 1000), rtol=1e-5
    #  )
