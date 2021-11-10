import pathlib
import shutil

import click
import lhapdf

from . import export, filter, load


@click.group()
def cli():
    pass


@cli.command("generate")
@click.argument("name")
@click.argument("labels", nargs=-1, type=int)
@click.option("-p", "--parent-pdf-set", default=None, help="parent pdf set")
@click.option("-a", "--all", is_flag=True, help="generate all the members")
@click.option("-i", "--install", is_flag=True, help="install into LHAPDF")
def generate_pdf(name, labels, parent_pdf_set, all, install):
    """Entry point to :func:`make_filter_pdf` and :func:`make_debug_pdf`"""

    pathlib.Path(name).mkdir(exist_ok=True)
    # labels = verify_labels(args.labels)
    # collect blocks
    all_blocks = []
    info = []
    if parent_pdf_set is None:
        # TODO use debug settings, i.e. x*(1-x) for everybody
        pass
    elif parent_pdf_set in ["toylh", "toy"]:  # from toy
        # TODO use Toy
        pass
    else:
        info = load.load_info_from_file(parent_pdf_set)
        # iterate on members
        for m in range(int(info["NumMembers"])):
            # blocks = load.load_blocks_from_file(parent_pdf_set, 0)
            all_blocks.append(load.load_blocks_from_file(parent_pdf_set, m))
            if not all:
                break
    # filter the PDF
    new_all_blocks = []
    for b in all_blocks:
        # new_blocks = filter.filter_pids(b, labels)
        new_all_blocks.append(filter.filter_pids(b, labels))
    # write
    export.dump_set(name, info, new_all_blocks)

    # install
    if install:
        run_install_pdf(name)


@cli.command("install")
@click.argument("name")
def install_pdf(name):
    """Entry point to :func:`run_install_pdf`"""
    run_install_pdf(name)


def run_install_pdf(name):
    """
    Install set into LHAPDF.

    The set to be installed has to be in the current directory.

    Parameters
    ----------
        name : str
            source pdf name
    """
    print(f"install_pdf {name}")
    target = pathlib.Path(lhapdf.paths()[0])
    src = pathlib.Path(name)
    if not src.exists():
        raise FileExistsError(src)
    shutil.move(str(src), str(target))


if __name__ == "__main__":
    cli()
