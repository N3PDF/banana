import pathlib
from jinja2 import Environment, FileSystemLoader


here = pathlib.Path(__file__).parent.absolute()
env = Environment(loader=FileSystemLoader(str(here)))


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


def dump_pdf(name, member, blocks):
    """
    Write LHAPDF data file

    Parameters
    ----------
        name : str
            target name
        blocks : list(dict)
            pdf blocks of data
    """
    
    target=pathlib.Path(name) / ("%s_%04d.dat"%(name,member))
    with open(target, "w") as o: 
        o.write("PdfType: central\nFormat: lhagrid1\n---\n")
        for b in blocks: 
            o.write(list_to_str(b["xgrid"])+"\n")
            o.write(list_to_str(b["Q2grid"])+"\n")
            o.write(list_to_str(b["pids"], "%d")+"\n")
            o.write(array_to_str(b["data"]))
            o.write("---\n")




