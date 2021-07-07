# -*- coding: utf-8 -*-
import pathlib

import yaml


def load_config(pkg_path):
    banana_cfg = {}
    with open(pkg_path / "banana.yaml", "r") as o:
        banana_cfg = yaml.safe_load(o)

    banana_cfg["dir"] = pkg_path

    for k in banana_cfg:
        if k[-5:] == "_path":
            banana_cfg[k] = pathlib.Path(banana_cfg["dir"]).absolute() / banana_cfg[k]

    return banana_cfg
