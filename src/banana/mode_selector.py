# -*- coding: utf-8 -*-
"""
Banana is driven by different "modes" that represent different configurations:

- different input databases
- (at the moment there is only a **single** output databas)
- different tables in the databases
- different entries in the tables
"""
import pathlib

import tinydb


class ModeSelector:
    """
    Holds (and opens) the correct databases according to the current mode.

    Parameters
    ----------
        cfg : dict
            banana configuration
        mode : str
            active mode
    """

    def __init__(self, cfg, mode):
        self.mode_cfg = cfg["modes"][mode]
        self.mode = mode
        # load DBs
        self.idb = tinydb.TinyDB(
            cfg["dir"] / cfg["data_dir"] / self.mode_cfg["input_db"]
        )
        self.odb = tinydb.TinyDB(cfg["dir"] / cfg["data_dir"] / "output.json")
