# -*- coding: utf-8 -*-
"""
toyLH pdf
---------
This routine returns the toyLH PDFs at the intitial scale
which is supposed to be Q = sqrt(2) GeV.
"""

import atexit


class toyPDFSet:
    """Fake PDF set"""

    name = "ToyLH"


class toyPDF:
    """Imitates lhapdf"""

    def __init__(self):
        self.N_uv = 5.107200e0
        self.auv = 0.8e0
        self.buv = 3e0
        self.N_dv = 3.064320e0
        self.adv = 0.8e0
        self.bdv = 4e0
        self.N_g = 1.7e0
        self.ag = -0.1e0
        self.bg = 5e0
        self.N_db = 0.1939875e0
        self.adb = -0.1e0
        self.bdb = 6e0
        self.fs = 0.2e0

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
        Q : float
            Squared energy (renormalization) scale.

        Returns
        -------
        float
            The value of xf(x,q2).
        """
        xuv = self.N_uv * x ** self.auv * (1e0 - x) ** self.buv
        xdv = self.N_dv * x ** self.adv * (1e0 - x) ** self.bdv
        xg = self.N_g * x ** self.ag * (1e0 - x) ** self.bg
        xdbar = self.N_db * x ** self.adb * (1e0 - x) ** self.bdb
        xubar = xdbar * (1e0 - x)
        xs = self.fs * (xdbar + xubar)
        xsbar = xs

        # Initialize PDFs to zero

        xpdf = {i: 0 for i in range(-6, 7)}

        if x > 1e0:
            return 0.0

        # assign
        xpdf[3] = xs
        xpdf[2] = xuv + xubar
        xpdf[1] = xdv + xdbar
        xpdf[21] = xpdf[0] = xg
        xpdf[-1] = xdbar
        xpdf[-2] = xubar
        xpdf[-3] = xsbar

        if pid not in xpdf:
            return 0.0
        return xpdf[pid]

    def xfxQ(self, pid, x, _Q):
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

        return self.xfxQ2(pid, x, _Q * _Q)

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
        return pid in [21] + list(range(-6, 6 + 1))


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


def ciao():
    """Print at exit."""
    print(
        """\nThanks for using toyPDF. Please make sure to close the door.\n"""
        + "\t" * 7
        + "__Alessandro"
    )


atexit.register(ciao)
