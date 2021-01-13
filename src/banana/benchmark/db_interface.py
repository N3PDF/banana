# -*- coding: utf-8 -*-


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
