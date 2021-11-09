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
@click.option("-i", "--install", is_flag=True, help="install into LHAPDF")
def generate_pdf(name, labels, parent_pdf_set, install):
    """Entry point to :func:`make_filter_pdf` and :func:`make_debug_pdf`"""
    # TODO allow to iterate ALL members

    pathlib.Path(name).mkdir(exist_ok=True)
    # labels = verify_labels(args.labels)
    # collect blocks
    if parent_pdf_set is None:
        # TODO use debug settings, i.e. x*(1-x) for everybody
        pass
    elif parent_pdf_set in ["toylh", "toy"]:  # from toy
        # TODO use Toy
        pass
    else:
        info = load.load_info_from_file(parent_pdf_set)
        blocks = load.load_blocks_from_file(parent_pdf_set, 0)
    # filter the PDF
    new_blocks = filter.filter_pids(blocks, labels)
    # write
    export.dump_set(name, info, [new_blocks])

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
