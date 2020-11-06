# -*- coding: utf-8 -*-
from contextlib import contextmanager
import os
from unittest import mock

import numpy as np
import lhapdf

from banana.data import generate_pdf

@contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)


def test_generate_pdf_debug(tmp_path):
    with cd(tmp_path):
        lhapdf.pathsPrepend(str(tmp_path))
        with mock.patch('sys.argv', ['',"test-d-bbar-only", "1", "-5"]):
            generate_pdf.generate_pdf()
            pdf = lhapdf.mkPDF("test-d-bbar-only", 0)
            for x in [.1, .2]:
                np.testing.assert_allclose(pdf.xfxQ2(21,x,1), 0.)
                np.testing.assert_allclose(pdf.xfxQ2(5,x,10), 0.)
                # we have to use large Q2
                # - otherwise lhapdf will crash us (and even there it is ...)
                np.testing.assert_allclose(pdf.xfxQ2(1,x,1000), x*(1.-x),rtol=1e-5)
                np.testing.assert_allclose(pdf.xfxQ2(-5,x,1000), x*(1.-x),rtol=1e-5)
