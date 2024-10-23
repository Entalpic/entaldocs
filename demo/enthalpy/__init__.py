"""
This is a top-level docstring for the ``enthalpy/`` package.

It contains, as expected, ``ReStructured Text`` markup.

.. tip::

    Make your documentation user-friendly, even for internal software!

.. note::

    This is a note about the package.

Usage
-----

.. code-block:: python

    from enthalpy import Entalpist

    entalpist = Entalpist(temperature=300, pressure=101325)
    print(entalpist.enthalpy())

In particular the enthalpy is calculated using the formula: $H = T * P$.
"""

from pathlib import Path

from enthalpy.entalpist import Entalpist

HOME = Path(__file__).parent.resolve()
"""
:py:class:`pathlib.Path`: Package constant describing where the package sits.

Use as :python:`from enthalpy import HOME`.
"""


def main():
    """
    Main function for the package.

    Using the :class:`~enthalpy.entalpist.Entalpist`, compute the enthalpy of a
    system (function: :meth:`~enthalpy.entalpist.Entalpist.enthalpy`).

    Returns
    -------
    None
    """
    print("Hello, world!")
    print(Entalpist.from_dict({"temperature": 300, "pressure": 101325}).enthalpy())
