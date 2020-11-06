# -*- coding: utf-8 -*-
from contextlib import contextmanager
import os
from unittest import mock

import numpy as np
import lhapdf

from banana.data import generate_pdf
from banana import toy

# thanks https://stackoverflow.com/questions/431684/how-do-i-change-the-working-directory-in-python/24176022#24176022
@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)

@contextmanager
def lhapdf_path(newdir):
    path = lhapdf.paths()
    lhapdf.pathsPrepend(str(newdir))
    try:
        yield
    finally:
        lhapdf.setPaths(path)


def test_generate_pdf_debug(tmp_path):
    with cd(tmp_path):
        with mock.patch('sys.argv', ['',"test-d-bbar-only", "1", "-5"]):
            generate_pdf.generate_pdf()
            with lhapdf_path(tmp_path):
                pdf = lhapdf.mkPDF("test-d-bbar-only", 0)
                for x in [.1, .2]:
                    np.testing.assert_allclose(pdf.xfxQ2(21,x,1), 0.)
                    np.testing.assert_allclose(pdf.xfxQ2(5,x,10), 0.)
                    # we have to use large Q2
                    # - otherwise lhapdf will crash us (and even there it is ...)
                    np.testing.assert_allclose(pdf.xfxQ2(1,x,1000), x*(1.-x),rtol=1e-5)
                    np.testing.assert_allclose(pdf.xfxQ2(-5,x,1000), x*(1.-x),rtol=1e-5)

def test_generate_pdf_toy(tmp_path):
    with cd(tmp_path):
        with mock.patch('sys.argv', ['',"test-toy-u-only", "-p", "toyLH", "2"]):
            generate_pdf.generate_pdf()
            with lhapdf_path(tmp_path):
                pdf = lhapdf.mkPDF("test-toy-u-only", 0)
                ref = toy.mkPDF("",0)
                for x in [.1, .2]:
                    np.testing.assert_allclose(pdf.xfxQ2(21,x,1), 0.)
                    np.testing.assert_allclose(pdf.xfxQ2(5,x,10), 0.)
                    # we have to use large Q2
                    # - otherwise lhapdf will crash us (and even there it is ...)
                    np.testing.assert_allclose(pdf.xfxQ2(2,x,1000), ref.xfxQ2(2,x,1000),rtol=1e-5)

def test_generate_pdf_parent(tmp_path):
    with cd(tmp_path):
        with mock.patch('sys.argv', ['',"test-NNPDF-g-only", "-p", "NNPDF31_nlo_as_0118", "21"]):
            generate_pdf.generate_pdf()
            with lhapdf_path(tmp_path):
                pdf = lhapdf.mkPDF("test-NNPDF-g-only", 0)
                ref = lhapdf.mkPDF("NNPDF31_nlo_as_0118",0)
                for x in [.1, .2]:
                    np.testing.assert_allclose(pdf.xfxQ2(1,x,1), 0.)
                    np.testing.assert_allclose(pdf.xfxQ2(5,x,10), 0.)
                    # we have to use large Q2
                    # - otherwise lhapdf will crash us (and even there it is ...)
                    np.testing.assert_allclose(pdf.xfxQ2(21,x,1000), ref.xfxQ2(21,x,1000),rtol=1e-5)
