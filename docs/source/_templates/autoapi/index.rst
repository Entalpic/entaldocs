.. Copyright 2025 Entalpic
API Reference
=============

This page contains leads to the documentation of the ``siesta`` package.

The API reference was auto-generated with ``autoapi`` [#f1]_.

You can see the source code on `Github <https://github.com/Entalpic/siesta>`_ and explore the rendered documentation here ⬇️

.. toctree::
   :titlesonly:

   {% for page in pages|selectattr("is_top_level_object") %}
   {{ page.include_path }}
   {% endfor %}

Installation
------------

Using siesta:

.. code-block:: bash

   $ uv tool install git+ssh://git@github.com/entalpic/siesta.git
   # then
   $ uv tool upgrade siesta

TL;DR
-----

.. code-block:: bash

   # 1️⃣ Start new project
   $ siesta project quickstart --local
   # 1️⃣ Initialize docs in existing project
   $ siesta docs init --local

   # 2️⃣ Build docs
   $ siesta docs build


Contributing
------------

.. code-block:: bash

   # 1️⃣ Clone the repository
   git clone git@github.com:Entalpic/siesta.git
   # or
   gh repo clone Entalpic/siesta

   # 2️⃣ Install the package
   uv tool install -e ./siesta
   # or
   pip install -e ./siesta


.. [#f1] Created with `sphinx-autoapi <https://github.com/readthedocs/sphinx-autoapi>`_
