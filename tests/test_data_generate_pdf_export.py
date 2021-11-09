# -*- coding: utf-8 -*-
import copy
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


def test_dump_info(tmp_path):
    with cd(tmp_path):
        with lhapdf_path(test_pdf):
            info = generate_pdf2.load.load_info_from_file("myCT14llo_NF3")
        info["SetDesc"] = "What ever I like"
        generate_pdf2.export.dump_info("new_pdf", info)
        with lhapdf_path(tmp_path):
            info2 = generate_pdf2.load.load_info_from_file("new_pdf")
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
            info = generate_pdf2.load.load_info_from_file("myCT14llo_NF3")
            blocks = generate_pdf2.load.load_blocks_from_file("myCT14llo_NF3", 0)
        new_blocks = copy.deepcopy(blocks)
        new_blocks[0]["xgrid"][0] = 1e-10
        generate_pdf2.export.dump_info("new_pdf", info)
        generate_pdf2.export.dump_blocks("new_pdf", 0, new_blocks)
        with lhapdf_path(tmp_path):
            blocks2 = generate_pdf2.load.load_blocks_from_file("new_pdf", 0)
            assert len(blocks) == len(blocks2)
            # my field is new
            np.testing.assert_allclose(blocks2[0]["xgrid"][0], 1e-10)
            # all the others are as before
            for k, v in blocks[0].items():
                if k == "xgrid":
                    continue
                np.testing.assert_allclose(v, blocks2[0][k])
            _pdf = lhapdf.mkPDF("new_pdf", 0)
