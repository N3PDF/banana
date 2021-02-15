# -*- coding: utf-8 -*-

import sqlite3
import pathlib
import abc
import subprocess
import itertools
import pickle

import rich
import rich.box
import rich.panel
import rich.progress
import rich.markdown
import sqlalchemy.orm

from .. import toy

from ..data import theories, sql, db


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
            print(f"PDFSet {pdf_name} is not installed! Installing now via lhapdf ...")
            res = subprocess.run(
                ["lhapdf", "get", pdf_name], check=True, capture_output=True
            )
            if len(res.stdout) == 0:
                raise ValueError("lhapdf could not install the set!")
            print(f"{pdf_name} installed.")
        pdf = lhapdf.mkPDF(pdf_name, 0)
    return pdf


default_cache = {"t_hash": b"", "o_hash": b"", "pdf": "", "external": "", "result": b""}
default_cache = dict(sorted(default_cache.items()))


default_log = {"t_hash": b"", "o_hash": b"", "pdf": "", "external": "", "log": b""}
default_log = dict(sorted(default_log.items()))


class CacheNotFound(LookupError):
    pass


class BenchmarkRunner:

    banana_cfg = {}
    """Global configuration"""

    external = ""
    """External reference program name"""

    console = rich.console.Console()

    db_base_cls = None
    """Base clase that describes db schema"""

    @abc.abstractstaticmethod
    def load_ocards(session, ocard_updates):
        """
        Load o-cards from the DB.

        Parameters
        ----------
            session : sqlalchemy.orm.session.Session
                DB session
            ocard_updates : list(dict)
                o-card configurations

        Returns
        -------
            ocards : list(dict)
                all requested o-cards
        """

    @abc.abstractmethod
    def run_me(self, theory, ocard, pdf):
        """
        Execute our program.

        Parameters
        ----------
            theory : dict
                theory card
            ocard : dict
                o card
            pdf : lhapdf_like
                PDF

        Returns
        -------
            me : dict
                our result
        """

    @abc.abstractmethod
    def run_external(self, theory, ocard, pdf):
        """
        Execute external program.

        Parameters
        ----------
            theory : dict
                theory card
            ocard : dict
                o card
            pdf : lhapdf_like
                PDF

        Returns
        -------
            me : dict
                external result
        """

    @abc.abstractmethod
    def log(self, theory, ocard, pdf, me, ext):
        """
        Create log from our and external result.

        Parameters
        ----------
            theory : dict
                theory card
            ocard : dict
                o card
            pdf : lhapdf_like
                PDF
            me : dict
                our result
            ext : dict
                external result

        Returns
        -------
            log : dict
                log
        """

    def db(self, db_path):
        """
        Open and eventually create the database

        Parameters
        ----------
            db_path : str
                path to database file

        Returns
        -------
            session : sqlalchemy.orm.session.Session
                db session
        """
        engine = db.engine(db_path)
        # create the database if not existing
        if not pathlib.Path(db_path).exists():
            __import__("ipdb").set_trace()
            db.create_db(self.db_base_cls, engine)
        #
        self.db_base_cls.metadata.bind = engine
        session = sqlalchemy.orm.sessionmaker(bind=engine)()
        return session

    def load_external(self, session, t, o, pdf):
        """
        Look into the DB.

        Parameters
        ----------
            session : sqlalchemy.orm.session.Session
                db session
            t : dict
                theory card
            o : dict
                o-card
            pdf : lhapdf_like
                applied PDF

        Returns
        -------
            ext : dict
                exernal result if available
        """
        sql_tmpl = "SELECT result FROM cache WHERE t_hash=? AND o_hash=? AND pdf=? AND external=?"
        ext = None
        with conn:
            res = conn.execute(
                sql_tmpl, (t["hash"], o["hash"], pdf.set().name, self.external)
            )
            ext = res.fetchone()
        # if not found, raise an Error to be pythonic
        if ext is None:
            raise CacheNotFound
        return pickle.loads(ext[0])

    def insert_external(self, session, t, o, pdf):
        """
        Obtain an external run.

        Parameters
        ----------
            t : dict
                theory card
            o : dict
                o-card
            pdf_name : str
                applied PDF

        Returns
        -------
            ext : dict
                result
        """
        # obtain data
        ext = self.run_external(t, o, pdf)
        # create record
        record = {
            "t_hash": t["hash"],
            "o_hash": o["hash"],
            "pdf": pdf.set().name,
            "external": self.external,
            "result": ext,
        }
        serialized_record = sql.serialize(record)
        with conn:
            sql.insertmany(
                conn,
                "cache",
                sql.RecordsFrame(default_cache.keys(), [serialized_record]),
            )
        return ext

    def run_config(self, session, t, o, pdf_name):
        """
        Run a single configuration.

        Parameters
        ----------
            session : sqlalchemy.orm.session.Session
                db session
            t : dict
                theory card
            o : dict
                o-card
            pdf_name : str
                applied PDF
        """
        pdf = get_pdf(pdf_name)
        # get our result
        me = self.run_me(t, o, pdf)
        # get external from cache if possible
        try:
            ext = self.load_external(session, t, o, pdf)
            self.console.print("Cache contains the external result")
        except CacheNotFound:
            self.console.print("Compute external result")
            ext = self.insert_external(session, t, o, pdf)
        # create log
        log_record = self.insert_log(session, t, o, pdf, me, ext)
        print(log_record)  # TODO delegate to rich

    def insert_log(self, session, t, o, pdf, me, ext):
        """
        Obtain an external run.

        Parameters
        ----------
            t : dict
                theory card
            o : dict
                o-card
            pdf_name : str
                applied PDF
            me : dict
                our result
            ext : str
                external result

        Returns
        -------
            log_record : dict
                result
        """
        # obtain data
        log_record = self.log(t, o, pdf, me, ext)
        # create record
        record = {
            "t_hash": t["hash"],
            "o_hash": o["hash"],
            "pdf": pdf.set().name,
            "external": self.external,
            "log": log_record,
        }
        raw_records, rf = sql.prepare_records(default_log, [record])
        with conn:
            sql.insertnew(conn, "logs", rf)
        return raw_records[0]

    def run(self, theory_updates, ocard_updates, pdfs):
        """
        Execute a (power) set of configuration and compare.

        Parameters
        ----------
            theory_updates : list(dict)
                generated theories
            ocard_updates : list(dict)
                generated ocards
            pdfs : list(str)
                applied PDFs
        """
        # open db
        db_path = self.banana_cfg["database_path"]
        session = self.db(db_path)
        # init input
        ts = theories.load(conn, theory_updates)
        os = self.load_ocards(session, ocard_updates)
        # print some load informations
        self.console.print(
            rich.panel.Panel.fit(
                f"Theories: {len(ts)} OCards: {len(os)} PDFs: {len(pdfs)}",
                rich.box.HORIZONTALS,
            )
        )
        # iterate all combinations
        full = itertools.product(ts, os, pdfs)
        # for t, o, pdf_name in rich.progress.track(
        #    full, total=len(ts) * len(os) * len(pdfs), console=self.console
        # ):
        # TODO find a way to display 2 progress bars
        for t, o, pdf_name in full:
            self.console.print(
                f"Computing for theory=[b]{t['hash'].hex()[:7]}[/b], "
                + f"ocard=[b]{o['hash'].hex()[:7]}[/b] and pdf=[b]{pdf_name}[/b] ..."
            )
            self.run_config(session, t, o, pdf_name)
