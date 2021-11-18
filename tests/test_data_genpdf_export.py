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


def test_dump_info(tmp_path):
    with cd(tmp_path):
        with lhapdf_path(test_pdf):
            info = genpdf.load.load_info_from_file("myCT14llo_NF3")
        info["SetDesc"] = "What ever I like"
        genpdf.export.dump_info("new_pdf", info)
        with lhapdf_path(tmp_path):
            info2 = genpdf.load.load_info_from_file("new_pdf")
            # my field is new
            assert info2["SetDesc"] == "What ever I like"
            # all the others are as before
            for k, v in info.items():
                if k == "SetDesc":
                    continue
                assert v == info2[k]


def test_dump_blocks(tmp_path):
    with cd(tmp_path):
        with lhapdf_path(test_pdf):
            info = genpdf.load.load_info_from_file("myCT14llo_NF3")
            blocks = genpdf.load.load_blocks_from_file("myCT14llo_NF3", 0)[1]
        new_blocks = copy.deepcopy(blocks)
        new_blocks[0]["xgrid"][0] = 1e-10
        heads = ["Debug\n"]
        genpdf.export.dump_set("new_pdf", info, [new_blocks], pdf_type_list=heads)
        with lhapdf_path(tmp_path):
            dat = genpdf.load.load_blocks_from_file("new_pdf", 0)
            head = dat[0]
            # testing overwriting of central member head
            assert head == "PdfType: central\n"
            blocks2 = dat[1]
            assert len(blocks) == len(blocks2)
            # my field is new
            np.testing.assert_allclose(blocks2[0]["xgrid"][0], 1e-10)
            # all the others are as before
            for k, v in blocks[0].items():
                if k == "xgrid":
                    continue
                np.testing.assert_allclose(v, blocks2[0][k])
            _pdf = lhapdf.mkPDF("new_pdf", 0)
