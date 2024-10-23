API Reference
=============

This page contains leads to the documentation of the demo ``enthalpy`` package.

The API reference was auto-generated with ``autoapi`` [#f1]_. See *𝚫 Entalpic Develoment Guidelines*'s source ``conf.py`` file for how to replicate configuration.

You can see the source code on Github(link todo) and explore the rendered documentation here ⬇️

.. toctree::
   :titlesonly:

   {% for page in pages|selectattr("is_top_level_object") %}
   {{ page.include_path }}
   {% endfor %}

.. [#f1] Created with `sphinx-autoapi <https://github.com/readthedocs/sphinx-autoapi>`_