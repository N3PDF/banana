# -*- coding: utf-8 -*-
"""
This module contains the Toy PDF.

It is defined at the initial scale :math:`Q = sqrt(2) GeV`.
"""


class toyPDFSet:
    """Fake PDF set"""

    name = "ToyLH"


class toyPDF:
    """Imitates a lhapdf.PDF"""

    def __init__(self):
        N_uv = 5.107200e0
        auv = 0.8e0
        buv = 3e0
        N_dv = 3.064320e0
        adv = 0.8e0
        bdv = 4e0
        N_g = 1.7e0
        ag = -0.1e0
        bg = 5e0
        N_db = 0.1939875e0
        adb = -0.1e0
        bdb = 6e0
        fs = 0.2e0

        xuv = lambda x: N_uv * x ** auv * (1e0 - x) ** buv
        xdv = lambda x: N_dv * x ** adv * (1e0 - x) ** bdv
        xg = lambda x: N_g * x ** ag * (1e0 - x) ** bg
        xdbar = lambda x: N_db * x ** adb * (1e0 - x) ** bdb
        xubar = lambda x: xdbar(x) * (1e0 - x)
        xs = lambda x: fs * (xdbar(x) + xubar(x))
        xsbar = xs

        self.xpdf = {}

        self.xpdf[3] = xs
        self.xpdf[2] = lambda x: xuv(x) + xubar(x)
        self.xpdf[1] = lambda x: xdv(x) + xdbar(x)
        self.xpdf[21] = self.xpdf[0] = xg
        self.xpdf[-1] = xdbar
        self.xpdf[-2] = xubar
        self.xpdf[-3] = xsbar

    def xfxQ2(self, pid, x, _Q2):
        """Get the PDF xf(x) value at (x,q2) for the given PID.

        Parameters
        ----------

        Parameters
        ----------
        pid : int
            PDG parton ID.
        x : float
            Momentum fraction.
        Q2 : float
            Squared energy (renormalization) scale.

        Returns
        -------
        float
            The value of xf(x,q2).
        """

        # Initialize PDFs to zero

        if x > 1e0:
            return 0.0

        if pid not in self.xpdf:
            return 0.0
        return self.xpdf[pid](x)

    def xfxQ(self, pid, x, Q):
        """Get the PDF xf(x) value at (x,q) for the given PID.

        Parameters
        ----------
        pid : int
            PDG parton ID.
        x : float
            Momentum fraction.
        Q : float
            Energy (renormalization) scale.

        Returns
        -------
        type
            The value of xf(x,q).
        """

        return self.xfxQ2(pid, x, Q * Q)

    def alphasQ(self, q):
        "Return alpha_s at q"
        return self.alphasQ2(q ** 2)

    def alphasQ2(self, _q2):
        "Return alpha_s at q2"
        return 0.35

    def set(self):
        "Return the corresponding PDFSet"
        return toyPDFSet()

    def hasFlavor(self, pid):
        """Contains a pdf for pid?"""
        return pid in ([21, 22] + list(range(-6, 6 + 1)))


def mkPDF(_setname, _member):
    """
    Factory functions for making single PDF members.

    Create a new PDF with the given PDF set name and member ID.

    Parameters
    ----------
    setname : type
        PDF set name.
    member : type
        Member ID.

    Returns
    -------
    toyPDF
        PDF object.
    """

    return toyPDF()
