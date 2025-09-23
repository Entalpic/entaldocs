# Copyright 2025 Entalpic
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import importlib

project = "siesta"  # Project name
copyright = "2025, Entalpic"
author = "Victor Schmidt <victor.schmidt@entalpic.ai>"  # Contributors to the package
release = importlib.metadata.version("siesta")

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx_design",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_math_dollar",
    "sphinx.ext.mathjax",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "autoapi.extension",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
    "sphinxext.opengraph",
    "code_include.extension",
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = []
rst_prolog = """
.. role:: python(code)
    :language: python
    :class: highlight
"""

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_title = (
    "siesta"  # Title for the HTML output for the docs, typically the project's name
)
html_theme = "shibuya"
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
html_js_files = ["js/custom.js"]
html_logo = "_static/img/entalpic-logo-rounded.png"
html_favicon = "_static/img/entalpic-logo-rounded-96.png"
html_theme_options = {
    "nav_links": [
        {
            "title": "siesta",
            "url": "index",
        },
        {
            "title": "GitHub Repository",
            "url": "https://github.com/Entalpic/siesta",
            "external": True,
        },
    ]
}

# html_baseurl = (
#     "file:///Users/victor/Documents/Github/entalpic/siesta/docs/build/html"
# )


# -----------------------------
# -----  Plugins configs  -----
# -----------------------------

# Napoleon
# https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html#configuration
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = False
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# https://www.sphinx-doc.org/en/master/usage/extensions/todo.html#directive-todo
todo_include_todos = True


# sphinx.ext.intersphinx
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "github": ("https://pygithub.readthedocs.io/en/stable/", None),
    "torch": ("https://pytorch.org/docs/stable/", None),
    "cyclopts": ("https://cyclopts.readthedocs.io/en/latest/", None),
}

# sphinx.ext.autodoc & autoapi.extension
# https://autoapi.readthedocs.io/
autodoc_typehints = "signature"
autoapi_type = "python"
autoapi_dirs = ["../../src/siesta"]  # list of paths to the packages to document
autoapi_ignore = ["*.venv/*", "*/tests/*", "*boilerplate/*"]
autoapi_member_order = "bysource"
autoapi_template_dir = "_templates/autoapi"
autoapi_python_class_content = "class"
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "imported-members",
]
autoapi_keep_files = False

# sphinx_math_dollar
# Note: CHTML is the only output format that works with \mathcal{}
mathjax_path = "https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_CHTML"
mathjax3_config = {
    "tex": {
        "inlineMath": [
            ["$", "$"],
            ["\\(", "\\)"],
        ],
        "processEscapes": True,
    },
    "jax": ["input/TeX", "output/CommonHTML", "output/HTML-CSS"],
}

# sphinx_autodoc_typehints
# https://github.com/tox-dev/sphinx-autodoc-typehints
typehints_fully_qualified = False
always_document_param_types = True
typehints_document_rtype = True
typehints_defaults = "comma"

# MyST
# https://myst-parser.readthedocs.io/en/latest/intro.html
myst_enable_extensions = ["colon_fence"]

# Hover X Ref
# https://sphinx-hoverxref.readthedocs.io/en/latest/index.html
hoverxref_auto_ref = True
hoverxref_mathjax = True

# Open Graph

ogp_site_url = "https://entalpic-siesta.readthedocs-hosted.com"
ogp_social_cards = {
    "enable": True,
    "image": "./_static/img/entalpic-logo-rounded.png",
}

# :siesta: <update>
# DO NOT change what is between <update> and </update>
# it may be overwritten in subsequent `siesta update` calls
# ----------------------------X---------------------------------


def skip_submodules(app, what, name, obj, skip, options):
    """Function used by ``autoapi-skip-member`` event to skip submodules.

    Parameters
    ----------
    app : Sphinx
        The Sphinx application object.
    what : str
        The type of the member.
    name : str
        The name of the member (like ``module.Class.attribute`` for instance).
    obj : object
        The Sphinx object representing the member.
    skip : bool
        Whether the member should be skipped (at this point, from the configuration).
    options : list[str]
        The options passed to the directive from ``conf.py``.

    Returns
    -------
    bool
        Whether the member should be skipped.
    """
    if what == "attribute":
        if obj.is_undoc_member:
            print(f"[siesta]  • Skipping {what} {name} because it is not documented.")
            return True
    return skip


def setup(sphinx):
    """Function to setup the Sphinx application.

    Parameters
    ----------
    sphinx : Sphinx
        The Sphinx application object.
    """
    sphinx.connect("autoapi-skip-member", skip_submodules)


# ----------------------------X---------------------------------
# :siesta: </update>
