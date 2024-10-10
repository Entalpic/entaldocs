API Reference
=============

This page contains auto-generated API reference documentation [#f1]_ for the Entalpic's Dev Guide ``demo`` package.

You can see the source code on Github(link todo) and explore the rendered documentation here ⬇️

.. toctree::
   :titlesonly:

   {% for page in pages|selectattr("is_top_level_object") %}
   {{ page.include_path }}
   {% endfor %}

.. [#f1] Created with `sphinx-autoapi <https://github.com/readthedocs/sphinx-autoapi>`_