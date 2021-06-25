# -*- coding: utf-8 -*-
"""
Auxilary module to generate some debug PDF which consist of selected pid of a parent set
"""
import argparse
import pathlib
import re
import shutil

import lhapdf
import numpy as np
from jinja2 import Environment, FileSystemLoader

from .. import toy
from . import basis_rotation as br

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
# fmt: off
custom_distribution = np.array([
    0, 0,0,0, 0,1,-4, 0, -4,1,0, 0,0,0
])
# fmt: on


def project_evol_basis(elems, elems_pids, requested_labels):
    """
    Project over evolution basis elements.

    Parameters
    ----------
        elems : list(float)
            parent flavor space values
        elems_pids : list(int)
            sorting of the parent values
        requested_labels : list(str)
            evolution distributions requested by the user

    Returns
    -------
        np.ndarray
            projected flavor space values
    """
    # cast the input to numpy to allow @
    elems = np.array(elems, dtype=float)
    pids_indices = [br.flavor_basis_pids.index(pid) for pid in elems_pids]
    # if custom is there, only return that one
    if "custom" in requested_labels:
        proj = (
            custom_distribution[:, np.newaxis]
            * custom_distribution
            / (custom_distribution @ custom_distribution)
        )
        return (proj[:, pids_indices] @ elems)[pids_indices]
    # map to evolution basis
    evol_elems = br.rotate_flavor_to_evolution[:, pids_indices] @ elems
    filtered_evol_elems = np.zeros_like(evol_elems)
    # keep only the elements requested by the user
    labels_indices = [br.evol_basis.index(lab) for lab in requested_labels]
    filtered_evol_elems[labels_indices] = evol_elems[labels_indices]
    # rotate back to flavor space
    flav_elems = np.linalg.inv(br.rotate_flavor_to_evolution) @ filtered_evol_elems
    return flav_elems[pids_indices]


def make_debug_pdf(name, active_labels, lhapdf_like=None):
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
    evol_basis = isinstance(active_labels[0], str)

    # check flavors
    if evol_basis:
        max_nf = 6
    else:
        max_nf = 3
        for q in range(4, 6 + 1):
            if q in active_labels or -q in active_labels:
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
    if not evol_basis:  # only pids are requested
        for pid in pids_out:
            if pid in active_labels:
                pdf_table.append(
                    [pdf_callable(pid, x, Q2) for x in xgrid for Q2 in Q2grid]
                )
            else:
                pdf_table.append([0.0 for _ in xgrid for _ in Q2grid])
    elif lhapdf_like is not None:
        pre_pdf_table = []
        for x in xgrid:
            for Q2 in Q2grid:
                elems = [pdf_callable(pid, x, Q2) for pid in pids_out]
                pre_pdf_table.append(project_evol_basis(elems, pids_out, active_labels))
        pdf_table = np.array(pre_pdf_table).T
    else:
        evol_pdf_table = []
        for pid in br.evol_basis:
            if pid in active_labels:
                evol_pdf_table.append(
                    [pdf_callable(pid, x, Q2) for x in xgrid for Q2 in Q2grid]
                )
            else:
                evol_pdf_table.append([0.0 for _ in xgrid for _ in Q2grid])
        pdf_table = np.linalg.inv(br.rotate_flavor_to_evolution) @ np.array(
            evol_pdf_table
        )
    # write to output
    dump_pdf(name, xgrid, Q2grid, pids_out, np.array(pdf_table).T)

    # make PDF.info
    description = f"'{name} PDFset, for debug purpose'"
    dump_info(name, description, pids_out)


def make_filter_pdf(name, active_labels, pdf_name):
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
    evol_basis = isinstance(active_labels[0], str)

    pdf = lhapdf.mkPDF(pdf_name)
    pdf_set = pdf.set().name
    src = pathlib.Path(lhapdf.paths()[0]) / pdf_set
    target = pathlib.Path(name)

    # copy info file
    with open(src / f"{pdf_set}.info") as info_f:
        info = info_f.read()
        if evol_basis:
            old_info = info
            info = re.sub(r"(ForcePositive:) \d", r"\1 0", info)
            if info == old_info:
                info += "ForcePositive: 0\n"
        with open(target / f"{name}.info", "w") as new_info_f:
            new_info_f.write(info)
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
            if evol_basis:
                new_elems = [
                    f"{x:.8e}" for x in project_evol_basis(elems, pids, active_labels)
                ]
            else:
                new_elems = []
                for pid, e in zip(pids, elems):
                    if pid in active_labels:
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


def pdf_label(arg):
    """
    Validate the input of argparse

    Parameters
    ----------
        arg : any
            input

    Returns
    -------
        value : int|str
            casted input

    Raises
    ------
        argparse.ArgumentTypeError :
            invalid argument
    """
    try:
        value = int(arg)
        if value not in br.flavor_basis_pids:
            raise ValueError
        return value
    except ValueError:
        if arg in br.flavor_basis_names:
            return br.flavor_basis_pids[br.flavor_basis_names.index(arg)]
        elif arg in br.evol_basis or arg == "custom":
            return arg
        else:
            raise argparse.ArgumentTypeError(
                f"'{arg}' is not a valid pdf label"
            )  # pylint: disable=raise-missing-from


def verify_labels(labels):
    """
    Check labels are consistent.

    Parameters
    ----------
        labels : list(str)
            input labels

    Returns
    -------
        list(str)
    """
    # all pids - good!
    if all(isinstance(lab, int) for lab in labels):
        return labels
    common_labels = {22: "ph", 21: "g"}
    try:
        labels = [common_labels[lab] if lab in common_labels else lab for lab in labels]
        pure_custom = "custom" in labels and len(labels) == 1
        pure_evol = (
            all(isinstance(lab, str) for lab in labels) and "custom" not in labels
        )
        if pure_custom or pure_evol:
            return labels
        raise TypeError
    except (KeyError, TypeError):
        raise SystemExit(  # pylint: disable=raise-missing-from
            "All the pdf labels should belong to the same basis (flavor or evolution)"
        )


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
    ap.add_argument("labels", type=pdf_label, help="active pdfs", nargs="+")
    ap.add_argument("-i", "--install", action="store_true", help="install into LHAPDF")
    args = ap.parse_args()
    print(args)
    pathlib.Path(args.name).mkdir(exist_ok=True)
    labels = verify_labels(args.labels)
    # find callable
    if args.from_pdf_set is None:
        pdf_set = None
        # create
        make_debug_pdf(args.name, labels, pdf_set)
    elif args.from_pdf_set.lower() in ["toylh", "toy"]:  # from toy
        pdf_set = toy.mkPDF("toyLH", 0)
        make_debug_pdf(args.name, labels, pdf_set)
    else:
        make_filter_pdf(args.name, labels, args.from_pdf_set)

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


if __name__ == "__main__":
    generate_pdf()
