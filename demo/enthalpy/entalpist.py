"""
Module-level documentation for the ``entalpist`` module.

.. hint::

    This is done by having a docstring at the top of the module.

.. important::

    You can reference external libraries as long as they are listed in the
    ``conf.py`` file (see ``intersphinx_mapping`` variable).

    Then ``:class:`pathlib.Path``` will link to the Python documentation:
    :class:`pathlib.Path`. Same for ``:func:`~torch.cuda.synchronize()```:
    :func:`~torch.cuda.synchronize()` (the ``~`` removes the dotted path to
    the referenced function / class / method and just displays its name).


----
"""


class Entalpist:
    def __init__(self, temperature, pressure=101325):
        """Class to calculate the enthalpy of a system.

        The enhalpy is calculated using the formula: $H = T * P$.

        Example
        -------
        >>> entalpist = Entalpist(300, 101325)
        >>> entalpist.enthalpy()
        30397500

        .. tip::

            Use the :meth:`Entalpist.from_dict` method to create an
            ``Entalpist`` object from a dictionary.

        Parameters
        ----------
        temperature : float
            The temperature of the system in Kelvin.
        pressure : float
            The pressure of the system in Pascal.
        """
        self.temperature = temperature
        self.pressure = pressure

    def enthalpy(self):
        """
        Calculate the enthalpy of the system.

        .. note::

            The enthalpy is in Joules.

        Returns
        -------
        float
            The enthalpy of the system.
        """
        return self.temperature * self.pressure

    def __str__(self):
        return (
            f"Entalpist(temperature={self.temperature}, pressure={self.pressure})"
            + f"Entalpist(temperature={self.temperature}, pressure={self.pressure})" + ", pressure, pressure, pressure, pressure, pressure"
        )

    @classmethod
    def from_dict(cls, data):
        return cls(data["temperature"], data["pressure"])

    @staticmethod
    def joules_to_kcal(joules):
        """Convert joules to kilocalories.

        Parameters
        ----------
        joules : float
            The amount of energy in joules.

        Returns
        -------
        float
            The amount of energy in kilocalories.

        Raises
        ------
        AssertionError
            If ``joules`` is not a number.
        """
        assert isinstance(joules, (int, float)), "joules must be a number"
        return joules / 4184


def compute_enthalpy(temperature, pressure):
    """Compute the enthalpy of a system.

    Parameters
    ----------
    temperature : float
        The temperature of the system in Kelvin.
    pressure : float
        The pressure of the system in Pascal.

    Returns
    -------
    float
        The enthalpy of the system.
    """
    return temperature * pressure
