import copy
import pathlib
import shutil

import lhapdf
import numpy as np
from eko import basis_rotation as br

from ... import toy
from . import export, load, project


def generate_pdf(
    name, labels, parent_pdf_set=None, members=False, info_update=None, install=False
):
    """
    Generate a new PDF from a parent PDF with a set of flavors.

    Parameters
    ----------
        name : str
            target name
        labels : list(int)
            list of flavors
        parent_pdf_set :
            parent PDF name
        all : bool
            iterate on members
        install : bool
            install on LHAPDF path
    Examples
    --------
        >>> generate_pdf(name, labels, {pid: f(x,Q2) for pid in mask})
            this will generate a PDF with a fixed function f(x,Q2) for every active flavor in mask
    """
    xgrid = np.geomspace(1e-9, 1, 240)
    Q2grid = np.geomspace(1.3, 1e5, 35)
    pathlib.Path(name).mkdir(exist_ok=True)
    # Checking label basis
    is_evol = False
    flavor_combinations = labels
    if project.is_evolution_labels(labels):
        is_evol = True
        flavor_combinations = project.evol_to_flavor(labels)
    elif project.is_pid_labels(labels):
        labels = np.array(labels, dtype=np.int_)
        flavor_combinations = project.pid_to_flavor(labels)

    # labels = verify_labels(args.labels)
    # collect blocks
    all_blocks = []
    info = None
    if parent_pdf_set is None:
        info = copy.deepcopy(load.template_info)
        all_blocks.append(
            [
                generate_block(
                    lambda _pid, x, _Q2: x * (1 - x),
                    xgrid,
                    Q2grid,
                    br.flavor_basis_pids,
                )
            ]
        )
    elif isinstance(parent_pdf_set, str):
        if parent_pdf_set in ["toylh", "toy"]:
            info = copy.deepcopy(load.Toy_info)
            toylh = toy.mkPDF("", 0)
            all_blocks.append(
                [generate_block(toylh.xfxQ2, xgrid, Q2grid, br.flavor_basis_pids)]
            )
        else:
            info = load.load_info_from_file(parent_pdf_set)
            # iterate on members
            for m in range(int(info["NumMembers"])):
                all_blocks.append(load.load_blocks_from_file(parent_pdf_set, m))
                if not members:
                    break
    elif isinstance(parent_pdf_set, dict):
        info = copy.deepcopy(load.template_info)
        all_blocks.append(
            [
                generate_block(
                    lambda pid, x, Q2: 0.0
                    if pid not in parent_pdf_set
                    else parent_pdf_set[pid](x, Q2),
                    xgrid,
                    Q2grid,
                    br.flavor_basis_pids,
                )
            ]
        )
    else:
        raise ValueError("Unknown parent pdf type")
    # filter the PDF
    new_all_blocks = []
    for b in all_blocks:
        new_all_blocks.append(project.project(b, flavor_combinations))

    # changing info file according to user choice
    if info_update is not None:
        if isinstance(info_update, dict):
            info.update(info_update)
        else:
            raise TypeError("Info to update are not in a dictionary format")
    # write
    info["Flavors"] = [int(pid) for pid in br.flavor_basis_pids]
    info["NumFlavors"] = len(br.flavor_basis_pids)
    if is_evol:
        info["ForcePositive"] = 0
    info["NumMembers"] = len(new_all_blocks)

    # exporting
    export.dump_set(name, info, new_all_blocks)

    # install
    if install:
        install_pdf(name)


def install_pdf(name):
    """
    Install set into LHAPDF.

    The set to be installed has to be in the current directory.

    Parameters
    ----------
        name : str
            source pdf name
    """
    print(f"install_pdf {name}")
    target = pathlib.Path(lhapdf.paths()[0])
    src = pathlib.Path(name)
    if not src.exists():
        raise FileExistsError(src)
    shutil.move(str(src), str(target))


def generate_block(xfxQ2, xgrid, Q2grid, pids):
    """
    Generate an LHAPDF data block from a callable

    Parameters
    ----------
        xfxQ2 : callable
            LHAPDF like callable
        Q2grid : list(float)
            Q2 grid
        pids : list(int)
            Flavors list
        xgrid : list(float)
            x grid

    Returns
    -------
        dict :
            PDF block
    """
    block = dict(Q2grid=Q2grid, pids=pids, xgrid=xgrid)
    data = []
    for x in xgrid:
        for Q2 in Q2grid:
            data.append(np.array([xfxQ2(pid, x, Q2) for pid in pids]))
    block["data"] = np.array(data)
    return block
