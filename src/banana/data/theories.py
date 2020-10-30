# -*- coding: utf-8 -*-
from datetime import datetime
import argparse
import pathlib
import copy

import numpy as np
import yaml

from . import card_generator
from . import power_set

here = pathlib.Path(__file__).parent


class TheoriesGenerator(card_generator.CardGenerator):
    """
    Generate all theories.

    Parameters
    ----------
        cfg : dict
            banana configuration
        mode : str
            active mode
    """

    table_name = "theories"

    def get_all(self):
        """Return a list of cards to be inserted."""
        # read template
        with open(here / "theory_template.yaml") as f:
            template = yaml.safe_load(f)
        # get all possible combinations
        full = power_set(self.mode_cfg[self.table_name])
        cards = []
        for config in full:
            template.update(config)
            cards.append(copy.copy(template))
        return cards
