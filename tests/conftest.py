# -*- coding: utf-8 -*-
import pathlib
import shutil
import sys

import pytest
import yaml


@pytest.fixture
def db():
    path = pathlib.Path.cwd() / "data"
    path.mkdir(parents=True)
    yield path
    shutil.rmtree(path)


@pytest.fixture
def banana_yaml(db):
    conf = pathlib.Path.cwd() / "banana.yaml"
    content = {
        "paths": {"database": str(db.absolute())},
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
