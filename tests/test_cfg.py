# -*- coding: utf-8 -*-
import pathlib
import tempfile

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
