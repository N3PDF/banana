# -*- coding: utf-8 -*-
"""Configurations related objects.

This module contains the functions used to manage configurations.
Moreover, the actual loaded configurations are stored in the module variable
:data:`cfg`, that is used as the source of truth for them.

"""
import pathlib

import appdirs
import yaml

cfg = None
"Global store for configurations"

default = {}

name = "banana.yaml"
"Configurations file conventional name"


def detect(path=None):
    """Search configurations file.

    It searches the configuration file in the following places, sorted:

    - provided path (e.g. CLI argument)
    - current directory
    - home directory
    - user default configurations directory
    - system default configurations directory

    If the path resolved is a directory (all cases but file path provided), it
    is assumed that the file name is that stored in the module level variable
    :data:`name`.

    Parameters
    ----------
    path: str ot os.PathLike
        path to a configuration file, or to a folder containing it

    Returns
    -------
    os.PathLike
        the resolved path

    Raises
    ------
    FileNotFoundError
        if the configuration file is not foundd in any of the places above

    """
    paths = []

    if path is not None:
        path = pathlib.Path(path)
        paths.append(path)

    paths.append(pathlib.Path.cwd())
    paths.append(pathlib.Path.home())
    paths.append(pathlib.Path(appdirs.user_config_dir()))
    paths.append(pathlib.Path(appdirs.site_config_dir()))

    for p in paths:
        configs_file = p / name if p.is_dir() else p

        if configs_file.is_file():
            return configs_file

    raise FileNotFoundError("No configurations file detected.")


def load(path):
    """Load configurations.

    Load everything as a dictionary.
    Determines `root` from the loaded dictionary:

    - if the key `root` is found in the configuration file, it is treated as an
      absolute path, or a relative one (relative to the configuration file
      parent folder)
    - otherwise `root` is assigned to the configuration file parent folder
      itself

    For the section `"path"`, all paths are converted to :class:`pathlib.Path`
    type, and (if not absolute) they are considered to be relative to `root`.

    No other conversion is performed.

    Parameters
    ----------
    path: str or os.PathLike
        configurations file path

    Returns
    -------
    dict
        loaded configurations

    """
    cfg = {}
    with open(path, "r", encoding="utf-8") as o:
        cfg = yaml.safe_load(o)

    try:
        root = pathlib.Path(cfg["root"])
        if not root.is_absolute():
            root = pathlib.Path(path).parent / root
    except KeyError:
        root = pathlib.Path(path).parent

    # convert loaded paths to pathlib.Path instances
    for name, lpath in cfg["paths"].items():
        lpath = pathlib.Path(lpath)
        cfg["paths"][name] = lpath if lpath.is_absolute() else root / lpath

    return cfg
