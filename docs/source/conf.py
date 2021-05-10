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
import sys

import sphinx_rtd_theme

sys.path.insert(0, os.path.abspath(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
))
# readthedocs.org/ cannot import physicslab directly.
# import physicslab  # nopep8
from physicslab import __version__ as physicslab_version  # nopep8
from physicslab import __author__ as physicslab_author  # nopep8


# -- Project information -----------------------------------------------------

project = 'Physics Lab'
copyright = '2020, Martin Brajer'
author = physicslab_author

# The full version, including alpha/beta/rc tags
version = release = physicslab_version


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosummary',
    "sphinx_rtd_theme",
]

autodoc_member_order = 'bysource'

# Add Python version number to the default address to correctly reference
# the Python standard library.
# See up-to-date intersphinx_mappings here:
# https://gist.github.com/bskinn/0e164963428d4b51017cebdb6cda5209
intersphinx_mapping = {
    'matplotlib': ('https://matplotlib.org/stable/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'python': ('https://docs.python.org/3.6', None),
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
