# -*- coding: utf-8 -*-
import datetime
import pathlib
import shutil
import sys

import pytest
import yaml


@pytest.fixture
def dbpath():
    path = (
        pathlib.Path.cwd() / f"data{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    )
    path.mkdir(parents=True)
    yield path
    shutil.rmtree(path)


@pytest.fixture
def banana_yaml(dbpath):
    conf = pathlib.Path.cwd() / "banana.yaml"
    content = {
        "paths": {"database": str(dbpath.absolute())},
        "input": {"tables": ["theories"]},
        "output": {"tables": ["cache"]},
    }
    conf.write_text(yaml.dump(content), encoding="utf-8")
    yield conf
    conf.unlink(missing_ok=True)


@pytest.fixture
def lhapdf():
    try:
        import lhapdf

        yield lhapdf
    except ModuleNotFoundError:

        class LHAPDF:
            _paths = []

            def paths(self):
                return self._paths

            def pathsPrepend(self, path):
                self._paths.insert(0, path)

            def setPaths(self, paths):
                self._paths = paths

        lhapdf = LHAPDF()
        sys.modules["lhapdf"] = lhapdf
        yield lhapdf
        del sys.modules["lhapdf"]
