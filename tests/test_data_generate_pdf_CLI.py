# -*- coding: utf-8 -*-

import numpy as np
import pytest
from click.testing import CliRunner
from utils import lhapdf_path, test_pdf

from banana.data.genpdf.cli import cli

# try:
#     import lhapdf
# except ImportError:
#     pytest.skip("No LHAPDF interface around", allow_module_level=True)
# TODO mark file skipped in coverage.py
lhapdf = pytest.importorskip("lhapdf")
runner = CliRunner()


def test_genpdf_messages():
    result = runner.invoke(cli, ["generate"])
    assert "Error: Missing argument 'NAME'." in result.output
    result = runner.invoke(cli, ["install"])
    assert "Error: Missing argument 'NAME'." in result.output
    result = runner.invoke(cli, ["generate", "--help"])
    assert "-p, --parent-pdf-set TEXT" in result.output
    assert "-a, --all" in result.output
    assert "-i, --install" in result.output
