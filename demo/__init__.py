"""
This is a top-level docstring for the ``demo/`` package.

It contains, as expected, ``ReStructured Text`` markup.

.. tip::

    Make your documentation user-friendly, even for internal software!
"""

from pathlib import Path

HOME = Path(__file__).parent.resolve()
"""
pathlib.Path: Package constant describing where the package sits.

Use as :python:`from demo import HOME`.
"""
