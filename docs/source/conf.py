# conf.py
import os
import sys
from datetime import datetime

import sphinx_bootstrap_theme

"""
conf.py

Sphinx configuration file for the ZimbeeCoin Zimbot project documentation.

This file contains configuration settings for Sphinx to generate documentation
from the project's source code and docstrings. It includes project information,
extensions, HTML output options, autodoc settings, and Napoleon for handling
Google and NumPy-style docstrings.

Key Configuration Sections:
- **Project Information**: Defines project name, author, version, and copyright.
- **Path Setup**: Adds the `src` directory to `sys.path` to enable Sphinx to find modules.
- **General Configuration**: Lists the Sphinx extensions used, such as `autodoc` for
  automatic documentation and `napoleon` for docstring support.
- **HTML Output Options**: Configures the HTML theme, static and template paths,
  and any specific HTML customization options.
- **Autodoc Options**: Specifies options for class member documentation ordering and type hint handling.
- **Napoleon Settings**: Configures parsing of Google and NumPy-style docstrings,
  with options to include/exclude private members and `__init__` docstrings.

Usage:
    This file is automatically used by Sphinx during the documentation build process.
    No direct execution is required.

Notes:
- This configuration file uses `sphinx_bootstrap_theme` for a responsive HTML theme.
- It leverages `sphinx_autodoc_typehints` to display Python type hints within descriptions.
- The `copybutton` extension is enabled to add a "copy" button to code blocks.
"""

# -- Path setup --------------------------------------------------------------

# Add the project's src directory to sys.path
sys.path.insert(0, os.path.abspath("../../src"))

# -- Project information -----------------------------------------------------

project = "ZimbeeCoin Zimbot"
author = "Michael Smith"
release = "0.1.0"
version = "0.1"  # Used by Sphinx for versioning
copyright = f"{datetime.now().year}, Michael Smith"

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",  # Standard documentation from docstrings
    "sphinx.ext.napoleon",  # Support for Google and NumPy style docstrings
    "sphinx_autodoc_typehints",  # Display type hints in documentation
    "sphinx_copybutton",  # Copy button for code blocks
    "sphinx.ext.viewcode",  # Link to highlighted source code
    "sphinx.ext.intersphinx",  # Linking between Sphinx documentation projects
]

# Configuration for intersphinx to link to Python standard library docs
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# Paths that contain templates, relative to this directory
templates_path = ["_templates"]

# Patterns to exclude from source file search
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

# Theme configuration using sphinx-bootstrap-theme
html_theme = "bootstrap"
html_theme_path = [sphinx_bootstrap_theme.get_html_theme_path()]

# Bootstrap theme options for Zimbot
html_theme_options = {
    "navbar_title": "ZimbeeCoin Zimbot",
    "navbar_site_name": "Site",
    "navbar_pagenav_name": "Page",
    "globaltoc_depth": 2,
    "navbar_links": [
        ("GitHub", "https://github.com/zimbeecoin/zimbot", True),
    ],
    "source_link_position": "footer",
}

# Path for custom static files (e.g., CSS), relative to this directory
html_static_path = ["_static"]

# -- Options for autodoc -----------------------------------------------------

# Control the order of autodoc member documentation
autodoc_member_order = "bysource"  # Documents members by their order in the source file

# Type hint configuration for autodoc
typehints_fully_qualified = False  # Do not fully qualify types in type hints

# -- Options for sphinx_autodoc_typehints ------------------------------------

# Display type hints inline with descriptions
autodoc_typehints = "description"

# -- Options for sphinx_copybutton -------------------------------------------

# Customize the copybutton regex to detect prompts in code blocks
copybutton_prompt_text = r"^\s*>?\s*"
copybutton_prompt_is_regexp = True

# -- Napoleon settings -------------------------------------------------------

# Napoleon extension settings for Google and NumPy style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False

# -- HTML theme specific options ---------------------------------------------

html_logo = "_static/logo.png"  # Specify logo file in _static
html_favicon = "_static/favicon.ico"  # Specify favicon file in _static

# -- Options for syntax highlighting -----------------------------------------

# Highlight code using the following style
pygments_style = "sphinx"

# -- Extension configurations ------------------------------------------------

# Customize for sphinx.ext.viewcode
viewcode_follow_imported_members = True

# -- Build configuration -----------------------------------------------------

# Enable build warnings as errors for stricter documentation checks
nitpicky = True
nitpick_ignore = []

# Custom values to override during specific builds
rst_epilog = """
.. |project| replace:: ZimbeeCoin Zimbot
.. |release| replace:: 0.1.0
"""

# -- End of conf.py ----------------------------------------------------------
