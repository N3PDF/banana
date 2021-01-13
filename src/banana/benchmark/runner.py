# -*- coding: utf-8 -*-

import sqlite3
import pathlib
import copy
import abc

import numpy as np
import pandas as pd
import pytest

from .. import toy

from ..data import power_set, theories, sql


def get_pdf(pdf_name):
    """
    Load PDF object from either LHAPDF or :mod:`toyLH`
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
    def generate_ocards(conn, ocard_updates):
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
        theories.generate(conn, theory_updates)
        self.generate_ocards(conn, ocard_updates)
