import copy

import numpy as np


def filter_pids(blocks, pids):
    """
    Filter only the given pids from the blocks.

    Parameters
    ----------
        blocks : list(dict)
            PDF blocks
        pids : list(int)
            surviving PIDs

    Returns
    -------
        list(dict) :
            filtered blocks
    """
    new_blocks = copy.deepcopy(blocks)
    for block in new_blocks:
        current_pids = block["pids"]
        current_data = block["data"].T
        new_data = []
        for pid, pdf in zip(current_pids, current_data):
            if pid in pids:
                new_data.append(pdf)
            else:
                new_data.append(np.zeros_like(pdf))
        block["data"] = np.array(new_data).T
    return new_blocks
