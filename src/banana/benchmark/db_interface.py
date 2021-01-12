# -*- coding: utf-8 -*-
import itertools
import datetime
import copy
import subprocess

import numpy as np
import pandas as pd
import tinydb
import pytest

import rich
import rich.box
import rich.panel
import rich.progress
import rich.markdown

from .. import toyLH
from .. import utils
from .. import mode_selector
from . import external



def get_pdf(pdf_name):
    """
    Load PDF object from either LHAPDF or :mod:`toyLH`
    """
    # setup PDFset
    if pdf_name == "ToyLH":
        pdf = toyLH.mkPDF("ToyLH", 0)
    else:
        import lhapdf  # pylint:disable=import-outside-toplevel

        # is the set installed? if not do it now
        if pdf_name not in lhapdf.availablePDFSets():
            print(f"PDFSet {pdf_name} is not installed! Installing now ...")
            subprocess.run(["lhapdf", "get", pdf_name], check=True)
            print(f"{pdf_name} installed.")
        pdf = lhapdf.mkPDF(pdf_name, 0)
    return pdf


class DBInterface(mode_selector.ModeSelector):
    """
    Interface to access DB

    Parameters
    ----------
        external : str
            program to compare to
    """

    def __init__(self, cfg, mode, external=None, assert_external=None):
        super().__init__(cfg, mode, external)
        self.assert_external = assert_external

        self.theory_query = tinydb.Query()
        self.o_query = tinydb.Query()

        self.defaults = {  # TODO move in banana.yaml
            "XIR": self.theory_query.XIR == 1.0,
            "XIF": self.theory_query.XIF == 1.0,
            "NfFF": self.theory_query.NfFF == 3,
            "FNS": self.theory_query.FNS == "FFNS",
            "DAMP": self.theory_query.DAMP == 0,
            "TMC": self.theory_query.TMC == 0,
        }

    def from_queries(self, theory_query, obs_query):
        """
        Retrieve (JSON) data form the DB using the queries
        """
        # TODO read table_names
        theories = self.idb.table("theories").search(theory_query)
        observables = self.idb.table("observables").search(obs_query)
        rich.print(
            rich.panel.Panel.fit(
                f" Theories: {len(theories)}\n" f" Observables: {len(observables)}",
                rich.box.HORIZONTALS,
            )
        )
        return theories, observables

    def update_default_queries(self, PTO, theory_update=None, o_query=None):
        """
        Build true queries out of the default settings using update dicts
        """
        # add PTO and build theory query
        if theory_update is None:
            theory_update = {}
        theory_update["PTO"] = self.theory_query.PTO == PTO
        theory = copy.deepcopy(self.defaults)
        theory.update(theory_update)
        theory_qres = self.theory_query.noop()
        for cond in theory.values():
            # skip empty ones
            if cond is None:
                continue
            theory_qres &= cond
        # build obs query
        if o_query is None:
            o_qres = self.o_query.prDIS.exists()
        self.t_qres = theory_qres
        self.o_qres = o_qres

    def run(self, pdfs):
        """
        Run a test matrix for the external program
        """
        theories, observables = self.from_queries(self.t_qres, self.o_qres)
        full = itertools.product(theories, observables)
        # for theory, obs in rich.progress.track(
        #     full, total=len(theories) * len(observables)
        # ):
        for theory, obs in full:
            # create our own object
            runner = Runner(theory, obs)
            for pdf_name in pdfs:
                pdf = get_pdf(pdf_name)
                # get our data
                yad_tab = runner.apply(pdf)
                # get external data
                if self.external == "APFEL":
                    from .external import (  # pylint:disable=import-error,import-outside-toplevel
                        apfel_utils,
                    )

                    ext_tab = external.get_external_data(
                        theory,
                        obs,
                        pdf,
                        self.idb.table("apfel_cache"),
                        apfel_utils.compute_apfel_data,
                    )
                elif self.external == "QCDNUM":
                    from .external import (  # pylint:disable=import-error,import-outside-toplevel
                        qcdnum_utils,
                    )

                    ext_tab = external.get_external_data(
                        theory,
                        obs,
                        pdf,
                        self.idb.table("qcdnum_cache"),
                        qcdnum_utils.compute_qcdnum_data,
                    )
                else:
                    raise ValueError(f"Unknown external {self.external}")

                # collect and check results
                log_tab = self._get_output_comparison(
                    theory,
                    obs,
                    yad_tab,
                    ext_tab,
                    self._process_external_log,
                    self.external,
                    self.assert_external,
                )

                # =============
                # print and log
                # =============
                log_tab["_pdf"] = pdf_name
                # print immediately
                self._print_res(log_tab)
                # store the log
                self._log(log_tab)

    @staticmethod
    def _process_external_log(yad, apf, external, assert_external):
        """
        Post-process the output log.
        """
        kin = dict()
        kin[external] = ref = apf["value"]
        kin["yadism"] = fx = yad["result"]
        kin["yadism_error"] = err = yad["error"]
        # test equality
        if assert_external is not False:
            if not isinstance(assert_external, dict):
                assert_external = {}
            assert (
                pytest.approx(
                    ref,
                    rel=assert_external.get("rel", 0.01),
                    abs=max(err, assert_external.get("abs", 1e-6)),
                )
                == fx
            )
        # compare for log
        with np.errstate(divide="ignore", invalid="ignore"):
            comparison = (fx / np.array(ref) - 1.0) * 100
        kin["rel_err[%]"] = comparison
        return kin

    def _get_output_comparison(
        self,
        theory,
        observables,
        yad_tab,
        other_tab,
        process_log,
        external=None,
        assert_external=None,
    ):
        rich.print(rich.markdown.Markdown("## Reporting results"))

        log_tab = {}
        # add metadata to log record
        rich.print(
            f"comparing for theory=[b]{theory.doc_id}[/b] and "
            f"obs=[b]{observables.doc_id}[/b] ..."
        )
        log_tab["_creation_time"] = datetime.datetime.now().isoformat()
        log_tab["_theory_doc_id"] = theory.doc_id
        log_tab["_observables_doc_id"] = observables.doc_id
        if isinstance(yad_tab, Exception):
            log_tab["_crash"] = yad_tab
            return log_tab
        # loop kinematics
        for sf in yad_tab:
            if not observable_name.ObservableName.is_valid(sf):
                continue
            kinematics = []
            for yad, oth in zip(yad_tab[sf], other_tab[sf]):
                # check kinematics
                if any([yad[k] != oth[k] for k in ["x", "Q2"]]):
                    raise ValueError("Sort problem: x and/or Q2 do not match.")
                # add common values
                kin = {}
                kin["x"] = yad["x"]
                kin["Q2"] = yad["Q2"]
                # preprocess assertion contraints
                if callable(assert_external):
                    assert_external_dict = assert_external(theory, observables, sf, yad)
                else:
                    assert_external_dict = assert_external
                # run actual comparison
                try:
                    kin.update(process_log(yad, oth, external, assert_external_dict))
                except AssertionError as e:
                    log_tab["_crash"] = e
                    log_tab["_crash_sf"] = sf
                    log_tab["_crash_kin"] = kin
                    log_tab["_crash_yadism"] = yad
                    log_tab["_crash_other"] = oth
                    log_tab["_crash_external"] = external
                    log_tab["_crash_assert_rule"] = assert_external_dict
                    # __import__("pdb").set_trace()
                    return log_tab
                kinematics.append(kin)
            log_tab[sf] = kinematics

        return log_tab

    def log(self, log_tab):
        """
        Dump comparison table.

        Parameters
        ----------
        log_tab :
            dict of lists of dicts, to be printed and saved in multiple csv
            files
        """

        # store the log of results
        crash_exception = log_tab.get("_crash", None)
        if crash_exception is not None:
            log_tab["_crash"] = str(type(crash_exception)) + ": " + str(crash_exception)
        new_id = self.odb.table("logs").insert(log_tab)
        rich.print(f"Added log with id={new_id}")
        # reraise exception if there is one
        if crash_exception is not None:
            raise crash_exception
