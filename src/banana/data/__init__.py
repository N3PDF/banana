# -*- coding: utf-8 -*-
"""
Module to collect utilites to help with the data generation:
"""
import itertools


def power_set(inp):
    """
    Compute the power set of a dictionary.

    Thank you: https://stackoverflow.com/questions/5228158/

    Parameters
    ----------
        inp : dict
            dictionary listing all posibilities

    Returns
    -------
        list(dict)
            power set of all possibilities, preserving the keys
    """
    return [
        dict(zip(inp.keys(), values)) for values in itertools.product(*inp.values())
    ]
