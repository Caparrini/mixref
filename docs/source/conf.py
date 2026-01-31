# Configuration file for the Sphinx documentation builder.

import os
import sys

# Add src to path for autodoc
sys.path.insert(0, os.path.abspath("../../src"))

# Import version from package
from mixref import __version__

# -- Project information -----------------------------------------------------
project = "mixref"
copyright = "2026, mixref"
author = "mixref"
release = __version__

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",  # Google-style docstrings
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_gallery.gen_gallery",
]

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# Suppress warnings
# Intersphinx warnings are expected in restricted environments
# Duplicate object warnings are from dataclass fields being documented as both class and instance attributes
suppress_warnings = [
    "config.cache",
    "intersphinx.external",
    "app.add_node",
    "app.add_directive",
    "app.add_role",
    "app.add_generic_role",
    "app.add_source_parser",
    "download.not_readable",
    "epub.unknown_project_files",
    "epub.duplicated_toc_entry",
    "autosummary",
    "autosectionlabel.*",
]

# Filter out dataclass duplicate warnings
nitpick_ignore = []
nitpick_ignore_regex = []

# -- Napoleon settings (Google-style docstrings) ----------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# -- Sphinx-Gallery configuration --------------------------------------------
sphinx_gallery_conf = {
    "examples_dirs": "examples",  # Path to example scripts
    "gallery_dirs": "auto_examples",  # Where to save gallery generated output
    "filename_pattern": "/plot_",  # Only run plot_*.py files
    "ignore_pattern": r"__init__\.py",
    "plot_gallery": "True",  # Execute examples
    "download_all_examples": False,
    "remove_config_comments": True,
    "expected_failing_examples": [],
    "min_reported_time": 0,
    "image_scrapers": ("matplotlib",),
    "reset_argv": lambda gallery_conf, script_vars: [],
}

# -- Intersphinx configuration -----------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "librosa": ("https://librosa.org/doc/latest/", None),
}

# Set a reasonable timeout for intersphinx to avoid long waits
intersphinx_timeout = 5

# -- Autodoc configuration ---------------------------------------------------
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}

# Skip imported members to avoid duplicate documentation
autodoc_class_signature = "separated"

# Autodoc type hints
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"

# Don't document imported members
def skip_imported_members(app, what, name, obj, skip, options):
    """Skip documentation of imported members to avoid duplicates."""
    # Skip dataclass internal attributes that cause duplicate warnings
    if name.split(".")[-1] in ("__dataclass_fields__", "__dataclass_params__", "__match_args__"):
        return True
    
    # Check if this is an imported member
    if what in ("class", "function", "method", "attribute"):
        # Get the module where the object is defined
        if hasattr(obj, "__module__"):
            obj_module = obj.__module__
            # Get the module being documented
            if hasattr(obj, "__objclass__"):
                doc_module = obj.__objclass__.__module__
            else:
                # For the current context, we need to get it from the name
                doc_module = ".".join(name.split(".")[:-1])
            
            # If they're different, skip this member (it's imported)
            if obj_module and doc_module and obj_module != doc_module:
                return True
    return skip

def setup(app):
    """Setup function for Sphinx."""
    app.connect("autodoc-skip-member", skip_imported_members)
    
    # Suppress duplicate object warnings from dataclasses
    import warnings
    def warning_filter(message, category=UserWarning, *args, **kwargs):
        message_str = str(message)
        # Don't show duplicate object description warnings from dataclass attributes
        if "duplicate object description" in message_str:
            return
        return warnings.showwarning(message, category, *args, **kwargs)
    
    warnings.showwarning = warning_filter
