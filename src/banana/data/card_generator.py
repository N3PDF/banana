# -*- coding: utf-8 -*-
from datetime import datetime
import argparse
import abc

from .. import mode_selector


class CardGenerator(mode_selector.ModeSelector, abc.ABC):
    """
    Generate all cards in the DB

    Parameters
    ----------
        cfg : dict
            banana configuration
        table : str
            target table
        mode : str
            active mode
    """

    @abc.abstractproperty
    def table_name(self):
        """target table name in the `input` database"""

    @abc.abstractmethod
    def get_all(self):
        """
        Return a list of cards to be inserted.

        Should be overwritten by child classes.

        Returns
        -------
            list
                list of cards
        """

    def write(self, cards):
        """
        Truncates the table and inserts the new cards.

        Parameters
        ----------
            cards : list
                list of cards
        """
        table = self.idb.table(self.table_name)
        table.truncate()
        # adjust creation time
        for c in cards:
            c["_created"] = datetime.now().isoformat()
        print(f"writing {len(cards)} cards to {self.table_name}")
        table.insert_multiple(cards)

    def fill(self):
        """
        Fill table in DB after asking for confirmation.
        """
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
        """
        Return the entry point to :meth:`fill`

        Parameters
        ----------
            cfg : dict
                banana configuration

        Returns
        -------
            callable
                entry point
        """

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