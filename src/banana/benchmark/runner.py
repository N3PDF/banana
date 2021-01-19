# -*- coding: utf-8 -*-

import sqlite3
import pathlib
import abc
import subprocess
import itertools

import rich
import rich.box
import rich.panel
import rich.progress
import rich.markdown

from .. import toy

from ..data import theories, sql


def get_pdf(pdf_name):
    """
    Load PDF object from either LHAPDF or :mod:`toyLH`

    Parameters
    ----------
        pdf_name : str
            pdf name

    Returns
    -------
        pdf : lhapdf_like
            PDF object
    """
    # setup PDFset
    if pdf_name == "ToyLH":
        pdf = toy.mkPDF("ToyLH", 0)
    else:
        import lhapdf  # pylint:disable=import-outside-toplevel

        # is the set installed? if not do it now
        if pdf_name not in lhapdf.availablePDFSets():
            print(f"PDFSet {pdf_name} is not installed! Installing now ...")
            subprocess.run(["lhapdf", "get", pdf_name], check=True)
            print(f"{pdf_name} installed.")
        pdf = lhapdf.mkPDF(pdf_name, 0)
    return pdf


class BenchmarkRunner:

    banana_cfg = {}

    @abc.abstractstaticmethod
    def init_ocards(conn):
        pass

    @abc.abstractstaticmethod
    def load_ocards(conn, ocard_updates, /):
        pass

    @abc.abstractmethod
    def run_me(self, theory, ocard, pdf, /):
        pass

    @abc.abstractmethod
    def run_external(self, theory, ocard, pdf, /):
        pass

    @abc.abstractmethod
    def log(self, theory, ocard, pdf, me, ext, /):
        pass

    def db(self, db_path):
        """
        Open and eventually create the database

        Parameters
        ----------
            db_path : str
                path to database file

        Returns
        -------
            conn : sqlite3.Connection
                db connection
        """
        # check the existence before opening, as sqlite creates an empty file by default
        init = not pathlib.Path(db_path).exists()
        conn = sqlite3.connect(db_path)
        if init:
            with conn:
                conn.execute(sql.create_table("theories", theories.default_card))
            self.init_ocards(conn)
            # init cache/logs
        return conn

    def run(self, theory_updates, ocard_updates, pdfs):
        # open db
        db_path = self.banana_cfg["database_path"]
        conn = self.db(db_path)
        # init input
        ts = theories.load(conn, theory_updates)
        os = self.load_ocards(conn, ocard_updates)
        # print some load informations
        # TODO delegate to console.print
        rich.print(
            rich.panel.Panel.fit(
                f" Theories: {len(ts)} OCards: {len(os)} PDFs: {len(pdfs)}",
                rich.box.HORIZONTALS,
            )
        )
        # iterate all combinations
        full = itertools.product(ts, os, pdfs)
        for t, o, pdf_name in rich.progress.track(
            full, total=len(ts) * len(os) * len(pdfs)
        ):
            rich.print(
                f"Computing for theory=[b]{t['ID']}[/b], "
                + f"ocard=[b]{o['prDIS']}[/b] and pdf=[b]{pdf_name}[/b] ..."
            )
            pdf = get_pdf(pdf_name)
            # get our result
            me = self.run_me(t, o, pdf)
            print(me)
            # get external from cache or whatever
            ext = self.run_external(t, o, pdf)
            print(ext)
            # create log
            log_record = self.log(t, o, pdf, me, ext)
            print(log_record)
