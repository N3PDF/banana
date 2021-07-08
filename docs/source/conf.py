# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import pathlib

import banana.version

here = pathlib.Path(__file__).parent

# -- Project information -----------------------------------------------------

project = "banana"
copyright = "2020-2021, N3PDF team"  # pylint: disable=redefined-builtin
author = "Felix Hekhorn, Alessandro Candido"

# The short X.Y version
version = banana.version.short_version
if not banana.version.is_released:
    version = "develop"

# The full version, including alpha/beta/rc tags
release = banana.version.full_version

here = pathlib.Path(__file__).parent

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx.ext.ifconfig",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.napoleon",
    "sphinxcontrib.bibtex",
    "sphinx.ext.extlinks",
]

# The master toctree document.
master_doc = "index"
bibtex_bibfiles = [str(p.relative_to(here)) for p in (here / "refs").glob("*.bib")]


# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["shared/*"]

# A string to be included at the beginning of all files
shared = pathlib.Path(__file__).absolute().parent / "shared"
rst_prolog = "\n".join([open(x).read() for x in os.scandir(shared)])

extlinks = {
    "yadism": ("https://n3pdf.github.io/yadism/%s", "yadism"),
    "eko": ("https://n3pdf.github.io/eko/%s", "eko"),
    "pineappl": ("https://n3pdf.github.io/pineappl/%s", "pineappl"),
    "pineko": ("https://github.com/N3PDF/pineko/%s", "pineko"),
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]


# -- Extension configuration -------------------------------------------------

autosectionlabel_prefix_document = True

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
# Thanks https://github.com/bskinn/sphobjinv
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/reference", None),
    "numpy": ("https://numpy.org/doc/stable", None),
}

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# https://github.com/readthedocs/readthedocs.org/issues/1139#issuecomment-312626491
def run_apidoc(_):
    import sys

    from sphinx.ext.apidoc import main

    sys.path.append(str(here.parent))
    # 'banana'
    docs_dest = here / "modules" / "banana"
    package = here.parents[1] / "src" / "banana"
    main(["--module-first", "-o", str(docs_dest), str(package)])
    (docs_dest / "modules.rst").unlink()


def setup(app):
    app.connect("builder-inited", run_apidoc)
