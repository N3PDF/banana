# -*- coding: utf-8 -*-
from unittest import mock
import pathlib

import yaml
import pytest

from banana import data as bdata
from banana.data import theories


@pytest.fixture
def banana_cfg(fs):
    fs.create_file('/tmp/input.json')
    fs.create_file('/tmp/output.json')
    fs.add_real_file(pathlib.Path(bdata.__file__).parent / "theory_template.yaml")
    cfg = {
        "dir": pathlib.Path("/tmp/"),
        "data_dir": ".",
        "input_tables": ["theories", "otest"],
        "modes": {"test": {"input_db": "input.json", "theories": {"PTO": [0, 1]}}},
    }
    return cfg


def test_run_parser_error(banana_cfg):
    gp = theories.TheoriesGenerator.get_run_parser(banana_cfg)
    with mock.patch("sys.argv", ["", "error"]):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            gp()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 2
        assert (
            str(pytest_wrapped_e.getrepr()).index(
                "argparse.ArgumentError: argument mode:"
            )
            > 0
        )


class MockArgs:
    mode = "test"


class MockAP:
    def add_argument(self, *args, **kwargs):
        pass

    def parse_args(self):
        return MockArgs()


def read_input(cur_banana_cfg):
    with open(
        cur_banana_cfg["dir"]
        / cur_banana_cfg["data_dir"]
        / cur_banana_cfg["modes"]["test"]["input_db"],
        "r",
    ) as o:
        inp = yaml.safe_load(o)
    return inp


def test_run_parser_empty(banana_cfg, monkeypatch):
    monkeypatch.setattr("argparse.ArgumentParser", MockAP)
    monkeypatch.setattr("builtins.input", lambda _: "n")
    gp = theories.TheoriesGenerator.get_run_parser(banana_cfg)
    gp()
    db = read_input(banana_cfg)
    assert db is None


def test_run_parser(banana_cfg, monkeypatch):
    monkeypatch.setattr("argparse.ArgumentParser", MockAP)
    monkeypatch.setattr("builtins.input", lambda _: "y")
    gp = theories.TheoriesGenerator.get_run_parser(banana_cfg)
    gp()
    db = read_input(banana_cfg)
    assert db is not None
    assert len(db["theories"]) == 2
