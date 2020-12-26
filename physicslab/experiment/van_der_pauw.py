"""
Van der Pauw resistivity measurement.

Four-point measurement bypass resistance of ohmic contacts.
"""


from enum import Enum

import numpy as np
from scipy.optimize import newton

import physicslab.utility


def solve_square(Rh, Rv):
    """Count sheet resistance from the given Pauw resistances.

    Accurate only for square sample: R_horizontal = R_vertical.

    :param Rh: Horizontal resistance
    :type Rh: float
    :param Rv: Vertical resistance
    :type Rv: float
    :return: Sheet resistance
    :rtype: float
    """
    R = (Rh + Rv) / 2
    van_der_pauw_constant = np.pi / np.log(2)
    Rs = R * van_der_pauw_constant
    return Rs


def solve_general(Rh, Rv, Rs=None):
    """Count sheet resistance from the given Pauw resistances.

    Universal formula.

    :param Rh: Horizontal resistance
    :type Rh: float
    :param Rv: Vertical resistance
    :type Rv: float
    :param Rs: Approximate value to start with. If :class:`None`,
        use :meth:`solve_square` to guess, defaults to None
    :type Rs: float or None, optional
    :return: Sheet resistance
    :rtype: float
    """
    if Rs is None:
        Rs = solve_square(Rh, Rv)
    #: Find root of :meth:`implicit_formula` near :param:`Rs`.
    Rs = newton(implicit_formula, Rs, args=(Rh, Rv), fprime=None)
    return Rs


def implicit_formula(Rh, Rv, Rs):
    """Van der Pauw measurement implicit function.

    | The function reads:
    | :math:`func(R_s) = exp(-\\pi R_v/R_s) + exp(-\\pi R_h/R_s) - 1`.
    | This function's roots give the solution.

    :param Rh: Horizontal resistance
    :type Rh: float
    :param Rv: Vertical resistance
    :type Rv: float
    :param Rs: Sheet resistance
    :type Rs: float
    :return: We choose the coefficients such that return value
        is zero
    :rtype: float
    """
    return np.exp(-np.pi * Rv / Rs) + np.exp(-np.pi * Rh / Rs) - 1


class Geometry(Enum):
    """ Resistance measurement configurations.

    Legend: :math:`R_{ij,kl} = V_{kl}/I_{ij}`. The contacts are numbered from
    1 to 4 in a counter-clockwise order, beginning at the top-left contact.
    See `Van der Pauw method
    <https://en.wikipedia.org/wiki/Van_der_Pauw_method#Reversed_polarity_measurements>`_
    at Wikipedia.
    """
    R1234 = '1234'
    R3412 = '3412'
    R2143 = '2143'
    R4321 = '4321'

    R2341 = '2341'
    R4123 = '4123'
    R3214 = '3214'
    R1432 = '1432'

    def _permutation_sign(self):
        """ Permutation sign of self.

        :return: Permutation sign of self.
        :rtype: float
        """
        return physicslab.utility.permutation_sign(self.value)

    def is_vertical(self):
        """ Find whether the geometry describes vertical configuration.

        :return: Is vertical?
        :rtype: bool
        """
        return self._permutation_sign() == 1

    def is_horizontal(self):
        """ Find whether the geometry describes horizontal configuration.

        :return: Is horizontal?
        :rtype: bool
        """
        return self._permutation_sign() == -1
