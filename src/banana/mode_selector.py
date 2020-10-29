# -*- coding: utf-8 -*-
import pathlib

import tinydb


class ModeSelector:
    """
    Handle the mode-related stuff

    Parameters
    ----------
        cfg : dict
            banana configuration
        mode : str
            active mode
        external : str
            external program name to compare to if in sandbox mode
    """

    def __init__(self, cfg, mode, external=None):
        self.mode_cfg = cfg["modes"][mode]
        self.mode = mode
        if self.mode_cfg["external"] is None:
            self.external = external
        else:
            if external is not None:
                raise ValueError(f"in {mode} mode you have {mode} as external")
            self.external = mode
        # load DBs
        self.idb = tinydb.TinyDB(
            cfg["dir"] / cfg["data_dir"] / self.mode_cfg["input_db"]
        )
        self.odb = tinydb.TinyDB(cfg["dir"] / cfg["data_dir"] / "output.json")
