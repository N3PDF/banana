# -*- coding: utf-8 -*-

import abc
import hashlib
import itertools
import pathlib
import pickle
import subprocess
from collections.abc import Iterable


import rich
import rich.box
import rich.markdown
import rich.panel
import rich.progress
import sqlalchemy.ext
import sqlalchemy.orm

from .. import toy
from ..data import db, dfdict, theories


def get_pdf(pdf_name, full_set=False):
    """
    Load PDF object from either LHAPDF or :mod:`toyLH`

    Parameters
    ----------
        pdf_name : str
            pdf name
        full_set: bool
            if True, return the full PDFs set with all the replicas

    Returns
    -------
        pdf : lhapdf_like
            PDF object
    """
    # setup PDFset
    if pdf_name == "ToyLH":
        pdf = toy.mkPDF("ToyLH", 0)
        if full_set:
            pdf = [pdf]
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
        if full_set:
            pdf = lhapdf.mkPDFs(pdf_name)
        else:
            pdf = lhapdf.mkPDF(pdf_name, 0)
    return pdf


def pdf_name(pdf):
    """
    Get the PDF set name

    Paramters
    ---------
        pdf: list(lhapdf_type), lhapdf_type
            pdf object or list

    Returns
    -------
        pdf_name: str
            PDF set name

    """
    if isinstance(pdf, Iterable):
        return pdf[0].set().name
    return pdf.set().name


default_cache = {"t_hash": b"", "o_hash": b"", "pdf": "", "external": "", "result": b""}
default_cache = dict(sorted(default_cache.items()))


default_log = {"t_hash": b"", "o_hash": b"", "pdf": "", "external": "", "log": b""}
default_log = dict(sorted(default_log.items()))


class BenchmarkRunner:

    banana_cfg = {}
    """Global configuration"""

    external = ""
    """External reference program name"""

    console = rich.console.Console()

    db_base_cls = None
    """Base class that describes db schema"""

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
            db.create_db(self.db_base_cls, engine)
        # make a session to the db and return it
        self.db_base_cls.metadata.bind = engine
        session = sqlalchemy.orm.sessionmaker(bind=engine)()
        return session

    def load_external(self, session, t, o, pdf_name):
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
            pdf_name : str
                applied PDF

        Returns
        -------
            ext : dict
                external result if available
        """
        ext = session.query(db.Cache).filter(
            db.Cache.t_hash == t["hash"],
            db.Cache.o_hash == o["hash"],
            db.Cache.pdf == pdf_name,
            db.Cache.external == self.external,
        )
        # if not found or multiple found, ext.one() will raise an Error
        return pickle.loads(ext.one().result)

    def insert_external(self, session, t, o, pdf):
        """
        Obtain an external run.

        Parameters
        ----------
        session : sqlalchemy.orm.session.Session
            DB ORM session
        t : dict
            theory card
        o : dict
            o-card
        pdf : str
            applied PDF

        Returns
        -------
        ext : dict
            result
        """
        # obtain data
        if isinstance(pdf, Iterable):
            ext = {}
            for n_rep, replica in enumerate(pdf):
                ext[n_rep] = self.run_external(t, o, replica)
        else:
            ext = self.run_external(t, o, pdf)
        record = {
            "t_hash": t["hash"],
            "o_hash": o["hash"],
            "pdf": pdf_name(pdf),
            "external": self.external,
            # TODO: pay attention, the hash will be computed on the binarized
            "result": pickle.dumps(ext),
        }
        # create record
        new_cache = db.Cache(
            **record, hash=hashlib.sha256(pickle.dumps(record)).digest().hex()
        )
        session.add(new_cache)
        # TODO: do we want to commit here or somewhere else?
        session.commit()
        return ext

    def run_config(self, session, t, o, pdf_name, use_replicas):
        """
        Run a single configuration.

        Parameters
        ----------
        session : sqlalchemy.orm.session.Session
            DB ORM session
        t : dict
            theory card
        o : dict
            o-card
        pdf_name : str
            applied PDF
        use_replicas: bool
            if True use the full PDF set
        """
        pdf = get_pdf(pdf_name, full_set=use_replicas)
        # get our result
        me = self.run_me(t, o, pdf)
        # get external from cache if possible
        try:
            ext = self.load_external(session, t, o, pdf_name)
            self.console.print("Cache contains the external result")
        except sqlalchemy.orm.exc.NoResultFound:
            self.console.print("Compute external result")
            ext = self.insert_external(session, t, o, pdf)
        # create log
        log_record = self.insert_log(session, t, o, pdf, me, ext)
        log_record.fancy()

    def insert_log(self, session, t, o, pdf, me, ext):
        """
        Obtain an external run.

        Parameters
        ----------
        session : sqlalchemy.orm.session.Session
            DB ORM session
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
        # TODO: quickfix for different eko/yadism format
        log_record = self.log(t, o, pdf, me, ext)
        if isinstance(log_record, dfdict.DFdict):
            log_document = log_record.to_document()
        else:
            log_document = dict(
                map(lambda t: (t[0], t[1].to_document()), log_record.items())
            )

        # create record
        record = {
            "t_hash": t["hash"],
            "o_hash": o["hash"],
            "pdf": pdf_name(pdf),
            "external": self.external,
            # TODO: pay attention, the hash will be computed on the binarized
            "log": pickle.dumps(log_document),
        }
        log_hash = hashlib.sha256(pickle.dumps(record)).digest().hex()
        new_log = db.Log(
            **record,
            hash=log_hash,
        )
        try:
            session.add(new_log)
            session.commit()
            print(f"\nLog added, hash={log_hash}\n")
        except sqlalchemy.exc.IntegrityError:
            session.rollback()
            # TODO update atime
            print(f"\nLog already present, hash={log_hash}\n")
        return log_record

    def run(self, theory_updates, ocard_updates, pdfs, use_replicas=False):
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
            use_replicas : bool
                if True use the full PDFs set

        """
        # open db
        db_path = self.banana_cfg["database_path"]
        session = self.db(db_path)
        # init input
        ts = theories.load(session, theory_updates)
        os = self.load_ocards(session, ocard_updates)
        # print some load information
        self.console.print(
            rich.panel.Panel.fit(
                f"Theories: {len(ts)} OCards: {len(os)} PDFs: {len(pdfs)} ext: {self.external}",
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
                f"Computing for theory=[b]{t['hash'][:7]}[/b], "
                + f"ocard=[b]{o['hash'][:7]}[/b] and pdf=[b]{pdf_name}[/b] ..."
            )
            self.run_config(session, t, o, pdf_name, use_replicas)
