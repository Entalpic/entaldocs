# Copyright 2025 Entalpic
r"""
.. _entaldocs-cli-tutorial:

EntalDocs CLI Tutorial
----------------------

This document provides a tutorial on how to use the ``entaldocs`` CLI tool to initialize
a Python project with standard 𝚫 Entalpic initial setup.

It also serves as a demo for how to write a Sphinx documentation project.

.. note::

    This tutorial assumes you have already installed the ``entaldocs`` package using
    ``pip`` or, preferably, ``uv``.


Getting Started
===============

The goal is to create a Python project with `uv
<https://docs.astral.sh/uv/getting-started/installation/>`_, install the necessary
dependencies for documentation, and set up the project's documentation.

.. code-block:: bash

    $ entaldocs quickstart-project --help # typically $ entaldocs quickstart-project --with-defaults

What happens is the following:

1. A new Python project is created in the current directory using ``uv``.
2. Using ``uv add``, common development dependencies are added to the project.
3. Pre-commit hooks to format and lint the code with ``ruff`` are added.
4. The project is initialized with ``entaldocs init-docs`` to create a ``docs/`` folder
   and install the necessary dependencies for documentation.


Docs Only
=========
If you already have a Python project and want to add documentation to it, you can use
the ``entaldocs init-docs`` command.

.. code-block:: bash

    $ entaldocs init-docs --help # typically $ entaldocs init-docs --uv --with-defaults

This creates a ``docs/`` folder in your project and installing the necessary
dependencies. Some of the contents of the ``docs/`` folder are copied from the Entalpic
Github repository and therefore requires you to set a Github Personal Access Token (PAT)
to access the files.

.. code-block:: bash

    $ entaldocs set-github-pat
    $ entaldocs init-docs --uv --with-defaults

Going further
=============

Currently ``entaldocs`` has 5 main commands:

- ``set-github-pat`` to set your Github Personal Access Token (PAT) to access remote
  files **required** for the ``entaldocs init-docs`` and ``entaldocs update`` commands.
- ``init`` to create a docs folder and get started with your current project's
  documentation.
- ``update`` to update the documentation boilerplate files in your project from Github.
- ``show-deps`` to show the dependencies that will be added to your project to make
  docs.
- ``quickstart-project`` to create a new Python project with ``uv`` and set up
  documentation as per ``init``.

.. tip::

    Add ``-h`` / ``--help`` flags to the above commands to get their own help messages

When running ``$ entaldocs init-docs`` the following happens:

1. Create a ``docs/`` folder (change with ``--path``)
2. Optionally install dependencies based on an interactive user choice (use ``--deps``
   to prevent prompt and install dependencies automatically)
3. Optionally use ``uv`` to install dependencies (use ``--uv`` to use ``uv`` without
   being asked)
4. By default, ``entaldocs`` will install the docs dependencies in the ``dev``
   dependencies. Use ``--as-main`` to install them as main dependencies.
5. ``entaldoc`` then prompts the user for the project name (default: current directory
   name) and the project's URL (default: ``https`` version of the current ``git`` remote
   URL)

.. warning::

    ``entaldocs`` will abort if the target folder already exists. Use ``--overwrite`` to
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

__version__ = importlib.metadata.version("entaldocs")
