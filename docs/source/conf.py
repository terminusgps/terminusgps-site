# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys

import django
from sphinxawesome_theme.postprocess import Icons

project = "terminusgps-site"
copyright = "2025, Terminus GPS"
author = "Terminus GPS"
release = "1.0.0"

sys.path.insert(0, os.path.abspath("../.."))
os.environ["DJANGO_SETTINGS_MODULE"] = "src.settings.dev"
django.setup()

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "autoclasstoc",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
]

intersphinx_mapping = {
    "python": ("http://docs.python.org/3", None),
    "boto3": (
        "https://boto3.amazonaws.com/v1/documentation/api/latest/",
        None,
    ),
    "django": (
        "http://docs.djangoproject.com/en/stable/",
        "http://docs.djangoproject.com/en/stable/_objects/",
    ),
}

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinxawesome_theme"
html_permalinks_icon = Icons.permalinks_icon
pygments_style = "sas"
pygments_style_dark = "lightbulb"
html_static_path = ["_static"]
