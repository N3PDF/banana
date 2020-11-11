# -*- coding: utf-8 -*-
"""
Auxilary module to generate some debug PDF which consist of selected pid of a parent set
"""
import pathlib
import argparse
import shutil
import re

import numpy as np

from jinja2 import Environment, FileSystemLoader
import lhapdf
from .. import toy

# ==========
# globals
# ==========


here = pathlib.Path(__file__).parent.absolute()
env = Environment(loader=FileSystemLoader(str(here)))


def _stringify(ls, fmt="%.6e"):
    """Stringify array"""
    return " ".join([fmt % x for x in ls])


def _stringify2(ls):
    """stringify array"""
    table = ""
    for line in ls:
        table += ("% .8e " % line[0]) + _stringify(line[1:], fmt="%.8e") + "\n"
    return table


# ==========
# dump
# ==========


def dump_pdf(name, xgrid, Q2grid, pids, pdf_table):
    """
    Write LHAPDF data file

    Parameters
    ----------
        name : str
            target name
        xgrid : list(float)
            target x-grid
        Q2grid : list(float)
            target Q2-grid
        pids: list(int)
            active pids
        pdf_table : numpy.ndarray
            pdf grid
    """
    # collect data
    data = dict(
        xgrid=_stringify(xgrid),
        Q2grid=_stringify(Q2grid),
        pids=_stringify(pids, fmt="%d"),
        pdf_table=_stringify2(pdf_table),
    )

    # ===========
    # apply template

    templatePDF = env.get_template("templatePDF.dat")
    stream = templatePDF.stream(data)
    stream.dump(str(pathlib.Path(name) / f"{name}_0000.dat"))


def dump_info(name, description, pids):
    """
    Write LHAPDF info file

    Parameters
    ----------
        name : str
            target name
        description : str
            description
        pids : list(int)
            active pids
    """
    # collect data
    data = dict(
        description=description,
        pids=pids,
    )

    # ===========
    # apply template

    templatePDF = env.get_template("templatePDF.info")
    stream = templatePDF.stream(data)
    stream.dump(str(pathlib.Path(name) / f"{name}.info"))


# ==========
# PDFs
# ==========


def make_debug_pdf(name, active_pids, lhapdf_like=None):
    """
    Create a new pdf.

    If the parent PDF is set to None (via `lhapdf_like`) the target
    functional form is set to :math:`xf(x) = x(1-x)`.

    Parameters
    ----------
        name : str
            target name
        active_pids : list(int)
            active pids
        lhapdf_like : None or object
            parent pdf
    """
    # check flavors
    max_nf = 3
    for q in range(4, 6 + 1):
        if q in active_pids or -q in active_pids:
            max_nf = q
    pids_out = list(range(-max_nf, 0)) + list(range(1, max_nf + 1)) + [21]
    # generate actual grids
    xgrid = np.geomspace(1e-9, 1, 240)
    Q2grid = np.geomspace(1.3, 1e5, 35)
    pdf_table = []
    # determine callable
    if lhapdf_like is None:
        pdf_callable = lambda pid, x, Q2: (1.0 - x) * x
    else:
        pdf_callable = lhapdf_like.xfxQ2
    # iterate partons
    for pid in pids_out:
        if pid in active_pids:
            pdf_table.append([pdf_callable(pid, x, Q2) for x in xgrid for Q2 in Q2grid])
        else:
            pdf_table.append([0.0 for x in xgrid for Q2 in Q2grid])
    # write to output
    dump_pdf(name, xgrid, Q2grid, pids_out, np.array(pdf_table).T)

    # make PDF.info
    description = f"'{name} PDFset, for debug purpose'"
    dump_info(name, description, pids_out)


def make_filter_pdf(name, active_pids, pdf_name):
    """
    Create a new pdf from a parent PDF.

    Parameters
    ----------
        name : str
            target name
        active_pids : list(int)
            active pids
        pdf_name : str
            parent pdf set from LHAPDF
    """
    pdf = lhapdf.mkPDF(pdf_name)
    pdf_set = pdf.set().name
    src = pathlib.Path(lhapdf.paths()[0]) / pdf_set
    target = pathlib.Path(name)
    # copy info file
    shutil.copy(str(src / f"{pdf_set}.info"), str(target / f"{name}.info"))
    # read actual file
    cnt = []
    with open(src / ("%s_%04d.dat" % (pdf_set, pdf.memberID)), "r") as o:
        cnt = o.readlines()
    zero = re.split(r"\s+", cnt[-2].strip())[0]
    # file head
    head_section = cnt.index("---\n")
    new_cnt = cnt[: head_section + 1]
    while head_section < len(cnt) - 1:
        # section head
        next_head_section = cnt.index("---\n", head_section + 1)
        new_cnt.extend(cnt[head_section + 1 : head_section + 4])
        # determine participating pids
        pids = np.array(cnt[head_section + 3].strip().split(" "), dtype=np.int_)
        # data
        for l in cnt[head_section + 4 : next_head_section]:
            elems = re.split(r"\s+", l.strip())
            new_elems = []
            for pid, e in zip(pids, elems):
                if pid in active_pids:
                    new_elems.append(e)
                else:
                    new_elems.append(zero)
            new_cnt.append((" ".join(new_elems)).strip() + "\n")
        new_cnt.append(cnt[next_head_section])
        # iterate
        head_section = next_head_section
    # write output
    with open(target / ("%s_%04d.dat" % (name, pdf.memberID)), "w") as o:
        o.write("".join(new_cnt))


def generate_pdf():
    """Entry point to :func:`make_filter_pdf` and :func:`make_debug_pdf`"""
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "name",
        type=str,
        help="pdf name",
    )
    ap.add_argument(
        "-p",
        "--from-pdf-set",
        type=str,
        help="parent pdf set",
    )
    ap.add_argument("pids", type=int, help="active pids", nargs="+")
    ap.add_argument("-i", "--install", action="store_true", help="install into LHAPDF")
    args = ap.parse_args()
    print(args)
    pathlib.Path(args.name).mkdir(exist_ok=True)
    # find callable
    if args.from_pdf_set == "toyLH":  # from toy
        pdf_set = toy.mkPDF("toyLH", 0)
        make_debug_pdf(args.name, args.pids, pdf_set)
    elif isinstance(args.from_pdf_set, str) and len(args.from_pdf_set) > 0:
        make_filter_pdf(args.name, args.pids, args.from_pdf_set)
    else:
        pdf_set = None
        # create
        make_debug_pdf(args.name, args.pids, pdf_set)
    # install
    if args.install:
        run_install_pdf(args.name)


def install_pdf():
    """Entry point to :func:`run_install_pdf`"""
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "name",
        type=str,
        help="pdf name",
    )
    args = ap.parse_args()
    run_install_pdf(args.name)


def run_install_pdf(name):
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
