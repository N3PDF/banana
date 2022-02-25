# -*- coding: utf-8 -*-
import pathlib
import random
import string
import tempfile

import pytest

import banana.cfg


def test_detect(banana_yaml):
    # check the one in the current directory
    assert banana_yaml == banana.cfg.detect()

    # check a random file, but explicitly specified as the config file
    with tempfile.NamedTemporaryFile() as fd:
        path = pathlib.Path(fd.name)
        assert path == banana.cfg.detect(path)

    # if not given, nor in the current folder, first fall-back has to be home
    # directory
    banana_yaml.unlink()
    path = pathlib.Path.home() / banana.cfg.name
    path.touch()
    assert path == banana.cfg.detect()
    path.unlink()

    # if no file detected, raises
    # (and if the filename is absurd, detection will be impossible)
    banana.cfg.name = "".join(random.choices(string.ascii_letters, k=100))
    with pytest.raises(FileNotFoundError, match="No configurations"):
        banana.cfg.detect()


def test_load():
    with tempfile.NamedTemporaryFile() as fd:
        path = pathlib.Path(fd.name)
        path.write_text("root: tempfile\npaths: {}\n", encoding="utf-8")
        banana.cfg.load(path)
