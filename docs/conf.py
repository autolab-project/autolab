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


with open("../autolab/version.txt", "r") as fh:
    version = fh.read().strip()

sys.path.insert(0, os.path.abspath('..'))

# use this command in the docs folder to create the html or pdf file:
# cd docs
# sphinx-build -b html . html
# sphinx-build -M latexpdf . latexpdf
# cd latexpdf/latex
# latexmk
# move autolab.pdf ..\..\..\autolab\autolab.pdf

# -- Project information -----------------------------------------------------

project = 'Autolab'
copyright = '2023, Quentin Chateiller & Bruno Garbin & Jonathan Peltier, (C2N-CNRS)'
author = 'Quentin Chateiller & Bruno Garbin & Jonathan Peltier'

# The full version, including alpha/beta/rc tags
release = version

# -- General configuration ---------------------------------------------------

master_doc = 'index'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []
