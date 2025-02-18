# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
from pathlib import Path

sys.path.insert(0, str(Path("../..", "terminusgps_tracker").resolve()))

project = "terminusgps-site"
copyright = "2024, Terminus GPS"
author = "Terminus GPS"
release = "1.0.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx_rtd_theme", "sphinx.ext.intersphinx", "sphinx.ext.autodoc"]

templates_path = ["_templates"]
exclude_patterns = []
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "django": (
        "https://docs.djangoproject.com/en/5.1/",
        "https://docs.djangoproject.com/en/5.1/_objects/",
    ),
}

autodoc_mock_imports = ["django", "boto3"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
