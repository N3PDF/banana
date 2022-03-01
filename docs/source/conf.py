# -*- coding: utf-8 -*-
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

here = pathlib.Path(__file__).parent

# -- Project information -----------------------------------------------------

project = "banana"
copyright = "2020-2022, banana team"  # pylint: disable=redefined-builtin
author = "banana team"

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
rst_prolog = "\n".join([open(x, encoding="utf-8").read() for x in os.scandir(shared)])

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

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    # "canonical_url": "",
    # "analytics_id": "UA-XXXXXXX-1",  #  Provided by Google in your dashboard
    # "logo_only": True,
    "display_version": True,
    # "prev_next_buttons_location": "bottom",
    # "style_external_links": False,
    # "vcs_pageview_mode": "",
    # "style_nav_header_background": "white",
    # # Toc options
    # "collapse_navigation": True,
    # "sticky_navigation": True,
    # "navigation_depth": 4,
    # "includehidden": True,
    # "titles_only": False,
}

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
    "numpy": ("https://numpy.org/doc/stable", None),
    "scipy": ("https://docs.scipy.org/doc/scipy", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable", None),
    "sqlalchemy": ("https://docs.sqlalchemy.org/en/14/", None),
}

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# https://github.com/readthedocs/readthedocs.org/issues/1139#issuecomment-312626491
def run_apidoc(_):
    import sys  # pylint: disable=import-outside-toplevel

    from sphinx.ext.apidoc import main  # pylint: disable=import-outside-toplevel

    sys.path.append(str(here.parent))
    # 'banana'
    docs_dest = here / "modules" / "banana"
    package = here.parents[1] / "src" / "banana"
    main(["--module-first", "-o", str(docs_dest), str(package)])
    (docs_dest / "modules.rst").unlink()


def setup(app):
    app.connect("builder-inited", run_apidoc)
