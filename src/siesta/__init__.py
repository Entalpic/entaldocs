# Copyright 2025 Entalpic
r"""
.. _siesta-cli-tutorial:

siesta CLI Tutorial
-------------------

**Siesta Is Entalpic'S Terminal Assistant.**

This document provides a tutorial on how to use the ``siesta`` CLI tool to initialize
a Python project with standard 𝚫 Entalpic initial setup.

It also serves as a demo for how to write a Sphinx documentation project.

.. note::

    This tutorial assumes you have already installed the ``siesta`` package using
    ``pip`` or, preferably, ``uv``.

TL;DR
------

**Start a new project from scratch:**

.. code-block:: bash

    # With local files (no GitHub PAT needed)
    $ siesta project quickstart --local

    # With most up to date remote files (requires GitHub PAT)
    $ siesta set-github-pat
    $ siesta project quickstart

**Add documentation to an existing project:**

.. code-block:: bash

    # Interactive setup
    $ siesta docs init

    # Non-interactive setup
    $ siesta docs init --with-defaults

**Work with documentation:**

.. code-block:: bash

    # Build docs locally
    $ siesta docs build

    # Watch for changes and auto-rebuild
    $ siesta docs watch

    # Update CSS/visual assets files from GitHub
    $ siesta docs update

Getting Started
===============

The goal is to create a Python project with `uv <https://docs.astral.sh/uv/getting-started/installation/>`_, install the necessary
dependencies for documentation, and set up the project's documentation.

For brand new projects, use the ``project`` command:

.. code-block:: bash

    # Look at your options
    $ siesta project quickstart --help
    # Then you would typically use the --with-defaults flag
    $ siesta project quickstart

What happens is the following:

1. A new Python project is created in the current directory using ``uv``.
2. Using ``uv add``, common development dependencies are added to the project.
3. Pre-commit hooks to format and lint the code with ``ruff`` are added.
4. The Sphinx documentation to automatically render docstrings is initialized with ``siesta docs init`` to create a ``docs/`` folder
   and install the necessary dependencies for documentation.


Docs Only
=========
If you already have a Python project and want to add documentation to it, you can use
the ``docs`` command with the ``init`` subcommand.

.. code-block:: bash


    $ siesta docs init --help
    $ siesta docs init --with-defaults

This creates a ``docs/`` folder in your project and installing the necessary
dependencies. Some of the contents of the ``docs/`` folder are copied from the Entalpic
Github repository and therefore requires you to set a Github Personal Access Token (PAT)
to access the files.

.. code-block:: bash

    $ siesta set-github-pat
    $ siesta docs init --uv --with-defaults

Going further
=============

Currently ``siesta`` has 4 main entry points with subcommands:

**Top-level commands:**
- ``set-github-pat`` to set your Github Personal Access Token (PAT) to access remote
  files.
- ``show-deps`` to show the dependencies that will be added to your project to make
  docs.

**``docs`` subcommands:**
- ``docs init`` to create a docs folder and get started with your current project's
  documentation.
- ``docs build`` to build the HTML documentation locally (equivalent to running
  ``make clean && make html`` in the docs folder).
- ``docs update`` to update the documentation boilerplate files in your project from Github. Typically updating the brand assets and colors.
- ``docs watch`` to automatically build the docs when source files are changed.

**``project`` subcommands:**
- ``project quickstart`` to create a new Python project with ``uv`` and set up
  documentation as per ``docs init``.

.. tip::

    Add ``-h`` / ``--help`` flags to the any ``siesta`` command to get its help message

.. note::

    ``docs init`` and ``docs update`` require a Github Personal Access Token (PAT) to
    access remote files. You can set it with ``$ siesta set-github-pat``. Alternatively,
    you can use the ``--local`` flag to use local files instead of fetching from Github.
    Note that it may therefore not use the most up-to-date files to render the docs.

When running ``$ siesta docs init`` the following happens:

1. Create a ``docs/`` folder (change with ``--path``)
2. Optionally install dependencies based on an interactive user choice (use ``--deps``
   to prevent prompt and install dependencies automatically)
3. Optionally use ``uv`` to install dependencies (use ``--uv`` to use ``uv`` without
   being asked)
4. By default, ``siesta`` will install the docs dependencies in the ``dev``
   dependencies. Use ``--as-main`` to install them as main dependencies.
5. ``siesta`` finally prompts the user for the project name (default: current directory
   name) and the project's URL (default: ``https`` version of the current ``git`` remote
   URL)

.. warning::

    ``siesta`` will abort if the target folder already exists. Use ``--overwrite`` to
    delete the folder if it exists before setting up the documentation.


.. tip::

    We won't need maths here, but if you wanted to, you could use ``$`` for
    inline-maths: $1 + e^{i\pi} = 0$ or ``$$`` for block-maths:
    $$
    \sum_{k=1}^{k=+\infty} \frac{1}{k^2} = \frac{\pi^2}{6}
    $$

.. important::

    Remember to use **raw** strings when you use maths: ``r"$1 + e^{i\pi} = 0$"`` or

    .. code-block:: python

        r'''
        $$
        1 + e^{i\pi} = 0
        $$
        '''

"""

import importlib.metadata

__version__ = importlib.metadata.version("siesta")

try:
    import os

    import ipdb  # noqa: F401

    # set ipdb as default debugger when calling `breakpoint()`
    os.environ["PYTHONBREAKPOINT"] = "ipdb.set_trace"
except ImportError:
    print(
        "ipdb not available. Consider adding it to your dev stack for a smoother debugging experience"
    )
