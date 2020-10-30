# -*- coding: utf-8 -*-
from datetime import datetime
import argparse
import copy
import abc

import numpy as np

from .. import mode_selector
from . import power_set


class CardGenerator(mode_selector.ModeSelector, abc.ABC):
    """
    Compile all cards to compare against

    Parameters
    ----------
        cfg : dict
            banana configuration
        table : str
            target table
        mode : str
            active mode
        external : str
            external program name to compare to if in sandbox mode
    """

    @abc.abstractproperty
    def table_name(self):
        pass

    def get_all(self):
        """Should return a list of cards"""
        return []

    def write(self, cards):
        """Insert all elements"""
        table = self.idb.table(self.table_name)
        table.truncate()
        # adjust creation time
        for c in cards:
            c["_created"] = datetime.now().isoformat()
        print(f"writing {len(cards)} cards to {self.table_name}")
        table.insert_multiple(cards)

    def fill(self):
        """Fill table in DB"""
        # check intention
        ask = input(f"Do you want to refill the {self.mode} {self.table_name}? [y/n]")
        if ask != "y":
            print("Nothing done.")
            return
        # load cards
        cards = self.get_all()
        # clear and refill
        self.write(cards)

    @classmethod
    def get_run_parser(cls, cfg):
        """get the entry point"""

        def run_parser():
            # setup
            ap = argparse.ArgumentParser()
            ap.add_argument(
                "mode",
                choices=cfg["modes"].keys(),
                help="input DB to fill",
            )
            # do it
            args = ap.parse_args()
            tg = cls(cfg, args.mode)
            tg.fill()

        return run_parser


class OCardGenerator(CardGenerator):
    def get_all_o(self, defaults):
        return []

    def get_all(self):
        """
        Collect all runcards

        Returns
        -------
            observables : list(dict)
                list of runcards
        """
        # default interpolation setup
        interpolation_xgrid = np.unique(
            np.concatenate([np.geomspace(1e-4, 0.15, 20), np.linspace(0.15, 1.0, 12)])
        )
        interpolation_polynomial_degree = 4
        interpolation_is_log = True
        defaults = dict(
            interpolation_xgrid=interpolation_xgrid.tolist(),
            interpolation_polynomial_degree=interpolation_polynomial_degree,
            interpolation_is_log=interpolation_is_log,
        )
        cards = self.get_all_o(defaults)
        return cards
