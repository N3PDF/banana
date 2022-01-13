import inspect

import IPython
from traitlets.config.loader import Config

from .navigator import NavigatorApp, c, l, o, t, table_objects
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
        "ls": app.list_all,
        "logs": app.show_full_logs,
        "dfl": app.log_as_dfd,
        "run": app.execute_runner,
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


def launch_navigator(pkg, bench=None):
    c = Config()
    banner = f"""
        Welcome to {pkg} benchmark skript!
        call yelp() or h() for a brief overview.
    """
    c.TerminalInteractiveShell.banner2 = inspect.cleandoc(banner) + "\n" * 2

    if bench is not None:
        init_cmds = [f"""from {bench}.navigator import *""", f"""from {pkg} import *"""]
    else:
        init_cmds = ["""from navigator import *""", f"""from {pkg} import *"""]
    args = ["--pylab"]
    for cmd in init_cmds:
        args.append(f"--InteractiveShellApp.exec_lines={cmd}")

    IPython.start_ipython(argv=args, config=c)
