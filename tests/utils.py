import os
import pathlib
from contextlib import contextmanager

import pytest

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
    paths = lhapdf.paths()
    lhapdf.pathsPrepend(str(newdir))
    try:
        yield
    finally:
        lhapdf.setPaths(paths)
