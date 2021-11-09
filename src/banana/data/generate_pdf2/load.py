import pathlib
import re

import lhapdf
import numpy as np


def load_blocks_from_file(pdfset_name, member):
    """
    Load a pdf from a parent pdf.

    Parameters
    ----------
        pdfset_name : str
            parent pdf name
        member : int
            pdf member

    Returns
    -------
        list(dict) :
            pdf blocks of data

    """
    pdf = lhapdf.mkPDF(pdfset_name, member)
    pdf_set = pdf.set().name
    src = pathlib.Path(lhapdf.paths()[0]) / pdf_set
    # read actual file
    cnt = []
    with open(src / ("%s_%04d.dat" % (pdf_set, pdf.memberID)), "r") as o:
        cnt = o.readlines()
    # file head
    head_section = cnt.index("---\n")
    blocks = []
    while head_section < len(cnt) - 1:
        # section head
        next_head_section = cnt.index("---\n", head_section + 1)
        # determine participating pids
        xgrid = np.array(cnt[head_section + 1].strip().split(" "), dtype=np.float_)
        Q2grid = np.array(cnt[head_section + 2].strip().split(" "), dtype=np.float_)
        pids = np.array(cnt[head_section + 3].strip().split(" "), dtype=np.int_)
        # data
        data = []
        for l in cnt[head_section + 4 : next_head_section]:
            elems = re.split(r"\s+", l.strip())
            elems = np.array(elems, dtype=np.float_)
            data.append(elems)
        blocks.append(dict(xgrid=xgrid, Q2grid=Q2grid, pids=pids, data=data))
        # iterate
        head_section = next_head_section
    return blocks
