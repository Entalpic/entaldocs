.. Copyright 2025 Entalpic
API Reference
=============

This page contains leads to the documentation of the ``$PROJECT_NAME`` package.

The API reference was auto-generated with ``autoapi`` [#f1]_.

You can see the source code on `Github <$PROJECT_URL>`_ and explore the rendered documentation here ⬇️

.. toctree::
   :titlesonly:

   {% for page in pages|selectattr("is_top_level_object") %}
   {{ page.include_path }}
   {% endfor %}

.. [#f1] Created with `sphinx-autoapi <https://github.com/readthedocs/sphinx-autoapi>`_