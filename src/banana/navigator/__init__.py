import inspect

import IPython
from traitlets.config.loader import Config

from .navigator import NavigatorApp, t, o, c, l
from .utils import compare_dicts

help_vars = f"""t = "{t}" -> query theories
    c = "{c}" -> query cache
    l = "{l}" -> query logs"""
help_fncs = """h() - this help
    m(str) - change mode
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
        "m": app.change_mode,
        "g": app.get,
        "ls": app.list_all,
        "truncate_logs": app.logs.truncate,
        "cmpt": lambda id1, id2: compare_dicts(app.get(t, id1), app.get(t, id2)),
    }

    mod.update(new_objs)


def launch_navigator(pkg, bench):
    c = Config()
    banner = f"""
        Welcome to {pkg} benchmark skript!
        call yelp() or h() for a brief overview.
    """
    c.TerminalInteractiveShell.banner2 = inspect.cleandoc(banner) + "\n" * 2

    init_cmds = [f"""from {bench}.navigator import *""", f"""from {pkg} import *"""]
    args = ["--pylab"]
    for cmd in init_cmds:
        args.append(f"--InteractiveShellApp.exec_lines={cmd}")

    IPython.start_ipython(argv=args, config=c)
