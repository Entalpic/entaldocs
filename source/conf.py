# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from pathlib import Path

project = "𝚫 Entalpic Develoment Guidelines"
copyright = "2024, Victor Schmidt"
author = "Victor Schmidt"
release = "0.1.0"

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
    "code_include.extension",
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

html_theme = "furo"
html_static_path = ["_static"]
html_title = "𝚫 Entalpic Develoment Guidelines"
html_css_files = [
    "css/custom.css",
]
# html_favicon = "./_static/images/logo.png"

# -----------------------------
# -----  Plugins configs  -----
# -----------------------------

# Napoleon
# https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html#configuration
napoleon_google_docstring = True
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


# Furo theme
# https://pradyunsg.me/furo/customisation/
html_theme_options = {
    # "top_of_page_button": None,
    "footer_icons": [
        {
            "name": "GitHub",
            "url": "https://github.com/entalpic/dev-guide",
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
            "class": "",
        },
    ],
}

# sphinx.ext.intersphinx
intersphinx_mapping = {
    "torch": ("https://pytorch.org/docs/stable", None),
    "python": ("https://docs.python.org/3", None),
    "omegaconf": ("https://omegaconf.readthedocs.io/en/latest", None),
}

# sphinx.ext.autodoc & autoapi.extension
# https://autoapi.readthedocs.io/
autodoc_typehints = "signature"
autoapi_type = "python"
autoapi_dirs = [str(Path(__file__).resolve().parent.parent / "demo")]
autoapi_ignore = ["*.venv/*", "*/tests/*"]
autoapi_member_order = "bysource"
autoapi_template_dir = "_templates/autoapi"
autoapi_python_class_content = "init"
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

ogp_site_url = "https://entalpic-dev-guide.readthedocs.io/en/latest/"
ogp_social_cards = {
    "enable": True,
    # "image": "./_static/images/logo.png",
}
