# -*- coding: utf-8 -*-
import pathlib
import shutil

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
    conf.unlink()
