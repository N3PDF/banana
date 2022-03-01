# -*- coding: utf-8 -*-
import pathlib

from . import cfg

__version__ = "0.0.0"


def register(path):
    """Register configurations.

    This function is provided for its simple heuristics for configuration file
    detection.
    The idea behind is that it can be invoked by runner scripts in the following
    way::

        import banana
        banana.register(__file__)

    Thus, if it's pointing to a file with a name different from the conventional
    one (see :data:`cfg.name`), it is assumed that this file is in the same
    folder of the configuration file, that is named with the conventional name.

    Parameters
    ----------
    path: str or os.PathLike
        a path pointing to configuration file, its parent directory, or another
        file in the same directory

    """
    path = pathlib.Path(path)

    if path.is_dir():
        path = path / cfg.name
    elif path.is_file():
        if path.name != cfg.name:
            path = path.parent / cfg.name
    else:
        raise ValueError("Path kind not supported")

    cfg.cfg = cfg.load(path)
