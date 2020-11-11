# -*- coding: utf-8 -*-
def compare_dicts(d1, d2, exclude_underscored=False):
    """
    Check which entries of the two dictionaries are different, and output
    the values.

    Parameters
    ----------
        d1 : dict
            first dict
        d2 : dict
            second dict
        exclude_underscored : bool
            skip keys prefixed with _?
    """
    kw = 20  # keys print width
    fw = 30  # values print width
    print("┌", "─" * (kw + 2), "┬", "─" * (fw * 2 + 1 + 2), "┐", sep="")
    for k in d1.keys() | d2.keys():
        if exclude_underscored and k[0] == "_":
            continue

        if k not in d1:
            print(f"│ {k:<{kw}} │ {None:>{fw}} {d2[k]:>{fw}} │")
        elif k not in d2:
            print(f"│ {k:<{kw}} │ {d1[k]:>{fw}} {None:>{fw}} │")
        elif d1[k] != d2[k]:
            print(f"│ {k:<{kw}} │ {d1[k]:>{fw}} {d2[k]:>{fw}} │")
    print("└", "─" * (kw + 2), "┴", "─" * (fw * 2 + 1 + 2), "┘", sep="")
