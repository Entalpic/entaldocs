.. Copyright 2025 Entalpic
API Reference
=============

This page contains leads to the documentation of the ``entaldocs`` package.

The API reference was auto-generated with ``autoapi`` [#f1]_.

You can see the source code on `Github <https://github.com/Entalpic/entaldocs>`_ and explore the rendered documentation here ⬇️

.. toctree::
   :titlesonly:

   {% for page in pages|selectattr("is_top_level_object") %}
   {{ page.include_path }}
   {% endfor %}

Installation
------------

Using Entaldocs:

.. code-block:: bash

   $ uv tool install git+ssh://git@github.com/entalpic/entaldocs.git
   # then
   $ uv tool upgrade entaldocs

TL;DR
-----

.. code-block:: bash

   # 1️⃣ Start new project
   $ entaldocs quickstart-project --local
   # 1️⃣ Initialize docs in existing project
   $ entaldocs init-docs --local

   # 2️⃣ Build docs
   $ entaldocs build-docs


Contributing
------------

.. code-block:: bash

   # 1️⃣ Clone the repository
   git clone git@github.com:Entalpic/entaldocs.git
   # or
   gh repo clone Entalpic/entaldocs

   # 2️⃣ Install the package
   uv tool install -e ./entaldocs
   # or
   pip install -e ./entaldocs


.. [#f1] Created with `sphinx-autoapi <https://github.com/readthedocs/sphinx-autoapi>`_
