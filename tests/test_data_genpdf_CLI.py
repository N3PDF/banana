# -*- coding: utf-8 -*-

import numpy as np
import pytest
from click.testing import CliRunner
from utils import cd, lhapdf_path, test_pdf

from banana.data.genpdf.cli import cli

# try:
#     import lhapdf
# except ImportError:
#     pytest.skip("No LHAPDF interface around", allow_module_level=True)
# TODO mark file skipped in coverage.py
lhapdf = pytest.importorskip("lhapdf")


def test_genpdf_CLI_messages():
    runner = CliRunner()
    result = runner.invoke(cli, ["generate"])
    assert "Error: Missing argument 'NAME'." in result.output
    result = runner.invoke(cli, ["install"])
    assert "Error: Missing argument 'NAME'." in result.output
    result = runner.invoke(cli, ["generate", "--help"])
    assert "-p, --parent-pdf-set TEXT" in result.output
    assert "-m, --members" in result.output
    assert "-i, --install" in result.output


def test_genpdf_CLI(tmp_path):
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["generate", "debug", "g"])
        assert result.exit_code == 0
        result1 = runner.invoke(cli, ["generate", "debug1", "21", "-p", "toy"])
        assert result1.exit_code == 0
        result2 = runner.invoke(cli, ["generate", "debug2", "21", "-p", "CT10", "-m"])
        assert result2.exit_code == 0
        d = tmp_path / "sub"
        d.mkdir()
        with lhapdf_path(d):
            result3 = runner.invoke(cli, ["generate", "debug3", "21", "-i"])
            assert result3.exit_code == 0
