import copy
import pathlib
import shutil

import lhapdf
import numpy as np

from ... import toy
from . import export, filter, load


def generate_pdf(name, labels, parent_pdf_set=None, all=False, install=False):
    """
    Generate a new PDF from a parent PDF with a set of flavours

    Parameters:
    -----------
        name : str
            target name
        labels : list(int)
            list of flavours
        parent_pdf_set : str
            parent PDF name
        all : bool
            iterate on members
        install : bool
            install on LHAPDF path
    """
    xgrid = np.geomspace(1e-9, 1, 240)
    Q2grid = np.geomspace(1.3, 1e5, 35)
    pathlib.Path(name).mkdir(exist_ok=True)
    labels = np.array(labels, dtype=np.int_)
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
                    labels,
                )
            ]
        )
    elif parent_pdf_set in ["toylh", "toy"]:
        info = copy.deepcopy(load.template_info)
        toylh = toy.mkPDF("", 0)
        all_blocks.append([generate_block(toylh.xfxQ2, xgrid, Q2grid, labels)])
    else:
        info = load.load_info_from_file(parent_pdf_set)
        # iterate on members
        for m in range(int(info["NumMembers"])):
            # blocks = load.load_blocks_from_file(parent_pdf_set, 0)
            all_blocks.append(load.load_blocks_from_file(parent_pdf_set, m))
            if not all:
                break
    # filter the PDF
    new_all_blocks = []
    for b in all_blocks:
        # new_blocks = filter.filter_pids(b, labels)
        new_all_blocks.append(filter.filter_pids(b, labels))
    # write
    export.dump_set(name, info, new_all_blocks)

    # install
    if install:
        run_install_pdf(name)


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

    Parameters:
    -----------
        xfxQ2 : callable
            LHAPDF like callable
        Q2grid : list(float)
            Q2 grid
        pids : list(int)
            Flavours list
        xgrid : list(float)
            x grid
    """
    block = dict(Q2grid=Q2grid, pids=pids, xgrid=xgrid)
    data = []
    for x in xgrid:
        for Q2 in Q2grid:
            data.append(np.array([xfxQ2(pid, x, Q2) for pid in pids]))
    block["data"] = np.array(data)
    return block
