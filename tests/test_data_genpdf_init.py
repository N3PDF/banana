# -*- coding: utf-8 -*-
import copy

import numpy as np
import pytest
from utils import cd, lhapdf_path, test_pdf

from banana.data import genpdf

# try:
#     import lhapdf
# except ImportError:
#     pytest.skip("No LHAPDF interface around", allow_module_level=True)
# TODO mark file skipped in coverage.py
lhapdf = pytest.importorskip("lhapdf")


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
