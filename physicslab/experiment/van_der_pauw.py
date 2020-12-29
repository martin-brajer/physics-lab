"""
Van der Pauw resistivity measurement.

Four-point measurement bypass resistance of ohmic contacts.
"""


import enum

import numpy as np
import pandas as pd
from scipy.optimize import newton as scipy_optimize_newton

import physicslab.utility
import physicslab.electricity as pl_el


def process(data):
    """ Bundle method.

    If :attr:`data` does include :data:`Measurement.RESISTANCE` column

    :param data: [description]
    :type data: pandas.DataFrame
    :return: Sheet resistance
    :rtype: float
    """
    measurement = Measurement(data)
    if measurement.resistance_isnull():
        measurement.find_resistances()
    Rh, Rv = measurement.split_and_average()
    return measurement.solve_for_sheet_resistance(Rh, Rv)


class Solve:
    """
    """

    @staticmethod
    def implicit_formula(Rs, Rh, Rv):
        """Van der Pauw measurement implicit function.

        | The function reads:
        | :math:`func(R_s) = exp(-\\pi R_v/R_s) + exp(-\\pi R_h/R_s) - 1`.
        | This function's roots give the solution.

        :param Rs: Sheet resistance. Solve for this, so MUST be first.
        :type Rs: float
        :param Rh: Horizontal resistance
        :type Rh: float
        :param Rv: Vertical resistance
        :type Rv: float
        :return: We choose the coefficients such that return value
            is zero
        :rtype: float
        """
        return np.exp(-np.pi * Rv / Rs) + np.exp(-np.pi * Rh / Rs) - 1

    @staticmethod
    def solve(Rh, Rv):
        Rs = Measurement.solve_square(Rh, Rv)
        return scipy_optimize_newton(
            implicit_formula, Rs, args=(Rh, Rv), fprime=None)

    @staticmethod
    def square(Rh, Rv):
        """ Compute sheet resistance from the given resistances.

        Accurate only for square sample: :math:`R_h = R_v`.

        :param Rh: Horizontal resistance
        :type Rh: float
        :param Rv: Vertical resistance
        :type Rv: float
        :return: Sheet resistance
        :rtype: float
        """
        R = (Rh + Rv) / 2
        van_der_pauw_constant = np.pi / np.log(2)
        return R * van_der_pauw_constant

    @staticmethod
    def general(Rh, Rv, Rs0):
        """ Compute sheet resistance from the given resistances.

        Universal formula.

        :param Rh: Horizontal resistance
        :type Rh: float
        :param Rv: Vertical resistance
        :type Rv: float
        :param Rs0: Approximate value to start with.
        :type Rs0: float
        :return: Sheet resistance
        :rtype: float
        """
        #: Find root of :meth:`implicit_formula` near :param:`Rs0`.
        return scipy_optimize_newton(
            Solve.implicit_formula, Rs0, args=(Rh, Rv), fprime=None)


class Measurement:
    """ Van der Pauw resistances measurements.

    :param data: [description], defaults to None
    :type data: pandas.DataFrame, optional
    """
    #: Class variable :data:`data`: geometry column name of
    #: type :class:`Geometry`.
    GEOMETRY = 'Geometry'
    #: Class variable :data:`data`: voltage column name of
    #: type :class:`float`.
    VOLTAGE = 'Voltage'
    #: Class variable :data:`data`: current column name of
    #: type :class:`float`.
    CURRENT = 'Current'
    #: Class variable :data:`data`: resistance column name of
    #: type :class:`float`.
    RESISTANCE = 'Resistance'

    def __init__(self, data=None):
        #: Measurement data as :class:`pandas.DataFrame`.
        self.data = None

        if data is None:
            self.data = pd.DataFrame(columns=self.get_columns())
        else:
            if self.GEOMETRY in data.columns:
                self.data = data
            else:
                raise AttributeError(
                    'Parameter :attr:`data` must at least include'
                    ' the "{}" column.'.format(self.GEOMETRY)
                )

    @classmethod
    def get_columns(cls):
        """ Columns of :data:`data`.

        :return: List of names. Actual names are saved in class variables.
        :rtype: list
        """
        return [cls.GEOMETRY, cls.VOLTAGE, cls.CURRENT, cls.RESISTANCE]

    def resistance_isnull(self):
        """ Resistance not exists or isnull.

        :return: [description]
        :rtype: bool
        """
        if self.RESISTANCE not in self.data.columns:
            return True
        return self.data[self.RESISTANCE].isnull().any()

    def find_resistances(self):
        """ Populate :attr:`data.RESISTANCE` using Ohm's law. """
        self.data[self.RESISTANCE] = pl_el.Resistance.from_ohms_law(
            self.data[self.VOLTAGE], self.data[self.CURRENT])

    def add(self, geometry, voltage, current):
        self.data = self.data.append({
            self.GEOMETRY: geometry,
            self.VOLTAGE: voltage,
            self.CURRENT: current
        }, ignore_index=True)

    def split_and_average(self):
        """

        :return: [description]
        :rtype: [type]
        """
        self.data[self.GEOMETRY] = self.data[self.GEOMETRY].apply(
            Geometry.classify)
        group = {
            Geometry.RHorizontal: [],
            Geometry.RVertical: [],
        }
        for i, row in self.data.iterrows():
            group[row[self.GEOMETRY]].append(row[self.RESISTANCE])
        return (
            np.average(group[Geometry.RHorizontal]),  # Rh
            np.average(group[Geometry.RVertical])  # Rv
        )

    def solve_for_sheet_resistance(self, Rh, Rv):
        """[summary]

        :param Rh: [description]
        :type Rh: [type]
        :param Rv: [description]
        :type Rv: [type]
        :return: [description]
        :rtype: [type]
        """
        Rs0 = Solve.square(Rh, Rv)
        sheet_resistance = Solve.general(Rh, Rv, Rs0)

        # Ratio of vertical and horizontal resistances.
        resistance_ratio = Rh / Rv
        if resistance_ratio < 1:
            resistance_ratio = 1 / resistance_ratio

        return sheet_resistance, round(resistance_ratio, ndigits=1)


class Geometry(enum.Enum):
    """ Resistance measurement configurations :class:`enum.Enum`.

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

    RVertical = '12'
    RHorizontal = '21'

    def _permutation_sign(self):
        """
        :return: Permutation sign of self.
        :rtype: float
        """
        return physicslab.utility.permutation_sign(self.value)

    def is_horizontal(self):
        """ Find whether the geometry describes horizontal configuration.

        :return: Is horizontal?
        :rtype: bool
        """
        return self._permutation_sign() == -1

    def is_vertical(self):
        """ Find whether the geometry describes vertical configuration.

        :return: Is vertical?
        :rtype: bool
        """
        return self._permutation_sign() == 1

    @staticmethod
    def _classify(geometry):
        """ Sort given Geometry to either vertical or horizontal group.

        :param geometry: Geometry to evaluate
        :type geometry: :class:`Geometry`
        :return: One of the two main configurations
        :rtype: :class:`Geometry`
        """
        if geometry.is_horizontal():
            return Geometry.RHorizontal
        else:
            return Geometry.RVertical

    @staticmethod
    def classify(geometry):
        """ Sort given Geometry to either vertical or horizontal group.

        :param geometry: Geometry to evaluate
        :type geometry: :class:`Geometry` or :class:`pandas.Series`
        :return: One of the two main directions
        :rtype: :class:`Geometry`
        """
        if isinstance(geometry, Geometry):
            return Geometry._classify(geometry)
        elif isinstance(geometry, pd.Series):
            return geometry.apply(Geometry._classify)
        else:
            raise NotImplemented
