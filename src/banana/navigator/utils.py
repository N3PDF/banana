# -*- coding: utf-8 -*-
def compare_dicts(
    d1, d2, exclude_underscored=False, key_width=20, value_width=30, exclude_keys=None
):
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
        key_width : int
            print width of key
        value_width : int
            print width of values
    """
    print("┌", "─" * (key_width + 2), "┬", "─" * (value_width * 2 + 1 + 2), "┐", sep="")
    for k in d1.keys() | d2.keys():
        if exclude_underscored and k[0] == "_":
            continue
        if exclude_keys is not None and k in exclude_keys:
            continue

        if k not in d1:
            print(f"│ {k:<{key_width}} │ {'':>{value_width}} {d2[k]:>{value_width}} │")
        elif k not in d2:
            print(f"│ {k:<{key_width}} │ {d1[k]:>{value_width}} {'':>{value_width}} │")
        elif d1[k] != d2[k]:
            print(
                f"│ {k:<{key_width}} │ {d1[k]:>{value_width}} {d2[k]:>{value_width}} │"
            )
    print("└", "─" * (key_width + 2), "┴", "─" * (value_width * 2 + 1 + 2), "┘", sep="")
