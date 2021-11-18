import os
import pathlib
from contextlib import contextmanager

import lhapdf

# import pytest

# TODO mark file skipped in coverage.py
# lhapdf = pytest.importorskip("lhapdf")
# lets follow the same spirit
@contextmanager
def lhapdf_path(newdir):
    paths = lhapdf.paths()
    lhapdf.pathsPrepend(str(newdir))
    try:
        yield
    finally:
        lhapdf.setPaths(paths)
