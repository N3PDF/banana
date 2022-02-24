# -*- coding: utf-8 -*-
import inspect

import IPython
from traitlets.config import loader

from .. import cfg
from .navigator import c, l, o, t
from .utils import compare_dicts

help_vars = f"""t = "{t}" -> query theories
    c = "{c}" -> query cache
    l = "{l}" -> query logs"""
help_fncs = """h() - this help
    ext(str) - change external
    g(tbl,id) - getter
    ls(tbl) - listing table with reduced informations"""


def register_globals(mod, app):
    new_objs = {
        # table short cuts
        "t": t,
        "o": o,
        "c": c,
        "l": l,
        # functions
        "ext": app.change_external,
        "g": app.get,
        "ga": app.get_all,
        "gbl": app.get_by_log,
        "ls": app.list_all,
        "logs": app.show_full_logs,
        "dfl": app.log_as_dfd,
        # "truncate_logs": app.logs.truncate,
        "diff": app.subtract_tables,
        "cmpt": lambda id1, id2: compare_dicts(
            app.get(t, id1), app.get(t, id2), exclude_keys=["uid", "hash", "ctime"]
        ),
        "cmpo": lambda id1, id2: compare_dicts(
            app.get(o, id1), app.get(o, id2), exclude_keys=["uid", "hash", "ctime"]
        ),
        "compare_dicts": compare_dicts,
        "simlogs": app.list_all_similar_logs,
        "compare": app.compare_external,
        "crashed_log": app.crashed_log,
    }

    mod.update(new_objs)


def launch_navigator(imports=None, cfg_path=None, skip_cfg=False, pylab=True):
    """Launch navigator.

    Parameters
    ----------
    imports: list(str)
        name of packages/modules to be imported (the whole content is directly
        imported in the global namespace); if ``None`` is considered to be
        empty (default: ``None``)
    cfg_path: str or os.PathLike
        path to configuration file or containing folder (if using the
        conventional name :data:`banana.cfg.name`); if ``None`` or pointing to a
        non-existing file, automatic detection is attempted (default: ``None``)
    skip_cfg: bool
        whether to skip configurations loading; useful if this function is
        invoked by a script, that is pre-loading configurations on its own
        (default: ``False``)
    pylab: bool
        whether to load :mod:`matplotlib.pylab` members in the global namespace
        (default: ``True``)

    """
    if not skip_cfg:
        # configurations are loaded, to support inbokation from the CLI
        cfg.cfg = cfg.load(cfg.detect(cfg_path))

    # update ipython configurations to add custom banner
    c = loader.Config()
    banner = """
        Welcome to banana's benchmark navigator!
        call yelp() or h() for a brief overview.
        """
    c.TerminalInteractiveShell.banner2 = inspect.cleandoc(banner) + "\n" * 2

    # set initial imports
    init_cmds = []
    if imports is None:
        imports = []

    for imp in imports:
        init_cmds.append(f"from {imp} import *")

    # add commands to be execute while entering
    args = []
    if pylab:
        args.append("--pylab")
    for cmd in init_cmds:
        args.append(f"--InteractiveShellApp.exec_lines={cmd}")

    # launch and enter interpreter
    IPython.start_ipython(argv=args, config=c)
