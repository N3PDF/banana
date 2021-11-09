import pathlib

import yaml


def list_to_str(ls, fmt="%.6e"):
    """
    Convert a list of numbers to a string

    Parameters
    ----------
        ls : list(float)
            list
        fmt : str
            format string

    Returns
    -------
        str :
            final string
    """
    return " ".join([fmt % x for x in ls])


def array_to_str(ar):
    """
    Convert an array of numbers to a string

    Parameters
    ----------
        ar : list(list(float))
            array

    Returns
    -------
        str :
            final string
    """
    table = ""
    for line in ar:
        table += ("% .8e " % line[0]) + list_to_str(line[1:], fmt="%.8e") + "\n"
    return table


def dump_blocks(name, member, blocks):
    """
    Write LHAPDF data file.

    Parameters
    ----------
        name : str
            target name
        member : int
            PDF member
        blocks : list(dict)
            pdf blocks of data
    """

    target = pathlib.Path(name) / ("%s_%04d.dat" % (name, member))
    target.parent.mkdir(exist_ok=True)
    with open(target, "w") as o:
        o.write("PdfType: central\nFormat: lhagrid1\n---\n")
        for b in blocks:
            o.write(list_to_str(b["xgrid"]) + "\n")
            o.write(list_to_str(b["Q2grid"]) + "\n")
            o.write(list_to_str(b["pids"], "%d") + "\n")
            o.write(array_to_str(b["data"]))
            o.write("---\n")


def dump_info(name, info):
    """
    Write LHAPDF info file.

    Parameters
    ----------
        name : str
            target name
        info : dict
            info dictionary
    """
    target = pathlib.Path(name) / ("%s.info" % (name))
    target.parent.mkdir(exist_ok=True)
    with open(target, "w") as o:
        yaml.safe_dump(info, o, default_flow_style=True, width=100000, line_break="\n")
    # TODO this creates at the moment an ugly 1 line file, which is working but unreadable ...


def dump_set(name, info, member_blocks):
    """
    Dump a whole set.

    Parameters
    ----------
        name : str
            target name
        info : dict
            info dictionary
        member_blocks : list(list(dict))
            blocks for all members
    """
    dump_info(name, info)
    for mem, blocks in enumerate(member_blocks):
        dump_blocks(name, mem, blocks)
