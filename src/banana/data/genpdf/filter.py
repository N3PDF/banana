import copy

import numpy as np

from .. import basis_rotation as br


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


def filter_evol(blocks, labels):
    """
    Filter in evolution basis from the blocks.

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
        if len(current_data) == 0:
            continue
        zeros = np.zeros_like(current_data[0])
        # load all flavors
        flavour_data = [zeros.copy() for pid in br.flavor_basis_pids]
        for pid, pdf in zip(current_pids, current_data):
            idx = br.flavor_basis_pids.index(pid)
            flavour_data[idx] = pdf
        # Rotate to evolution basis
        evol_data = br.rotate_flavor_to_evolution @ np.array(flavour_data)
        # Filter in evolution basis
        for pos, label in enumerate(br.evol_basis):
            if label not in labels:
                evol_data[pos] = zeros.copy()
        new_data = np.linalg.inv(br.rotate_flavor_to_evolution) @ evol_data
        block["pids"] = br.flavor_basis_pids
        block["data"] = np.array(new_data).T
    return new_blocks
