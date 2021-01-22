# -*- coding: utf-8 -*-
import pathlib
import yaml


def load_config(pkg_path):
    banana_cfg = {}
    with open(pkg_path / "banana.yaml", "r") as o:
        banana_cfg = yaml.safe_load(o)

    banana_cfg["dir"] = pkg_path
    return banana_cfg
