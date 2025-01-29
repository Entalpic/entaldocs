.. Copyright 2025 Entalpic
Example documentation file
==========================

This is an example documentation file that illustrates how to use ``.rst`` syntax to write documentation, including **tutorials**.

---

Include code to illustrate how to use the package / module / class / method / function etc.

Remember, this works in docstrings *and* in stand-alone ``.rst`` files.

.. code-block:: python

    import entaldocs

    entaldocs.cli.app()

.. note::

    This is a note. You can use it to add notes to your documentation.

.. warning::

    This is a warning. You can use it to add warnings to your documentation.

Cool features:

Reference code docs of:

- A class: :class:`entaldocs.logger.BaseLogger` (long format)
- Another class :class:`~entaldocs.logger.Logger` (short format, by prepending ``~``)
- A method :meth:`~entaldocs.logger.Logger.prompt`
- Or even an external library :class:`github.MainClass.Github`

.. note

    External content should be listed in ``docs/conf.py:intersphinx_mapping``.
    More info in the `Read The Docs documentation <https://docs.readthedocs.io/en/stable/guides/intersphinx.html>`_.

An actual tutorial on ``.rst``:
`ReStructured Text for those who know Markdown <https://docs.open-mpi.org/en/v5.0.x/developers/rst-for-markdown-expats.html#hyperlinks-to-urls>`_

.. important::

    Check out this documentation for more on the specific so-called *admonitions* like
    the "note", "warning", "important", etc. coloured boxes in this document:
    `Furo theme documentation <https://pradyunsg.me/furo/reference/admonitions/#supported-types>`_

.. attention::

    ReStructured Text is a bit more complicated than Markdown, but it's worth it.
    **One common mistake** is to forget that spaces and new lines matter in ``.rst``.
    For example, the following will not work:

    .. code-block::

        .. note::
        This is NOT a note.

    But this will

    .. code-block::

        .. note::

            This is a note.

    Same goes for whitespaces: ``.. code-block::`` ✅ ``..code-block::`` ❌.


.. todo::

    Improving the documentation: `Recommendations for Sphinx plugins <https://pradyunsg.me/furo/recommendations/>`_.

.. dropdown::  :octicon:`megaphone` Want to learn more?

    You can also have images!

    .. image:: https://picsum.photos/300
        :alt: A cute animal

    And icons :octicon:`project` and badges :bdg-primary:`primary`, :bdg-primary-line:`primary-line`

    Or emphasize a link:

    .. article-info::
        :avatar: https://raw.githubusercontent.com/tristandeleu/jax-dag-gflownet/master/_assets/dag_gflownet.png
        :avatar-link: https://www.youtube.com/watch?v=dQw4w9WgXcQ
        :avatar-outline: muted
        :author: Some Author
        :date: Jul 24, 2021
        :read-time: 5 min read
        :class-container: sd-p-2 sd-outline-muted sd-rounded-1

    This is all documented in `Sphinx-Design <https://sphinx-design.readthedocs.io/en/furo-theme/>`_.
