"""
Van der Pauw resistivity measurement.

| Four-point measurement bypass resistance of ohmic contacts.
| To find resistivity from sheet resistance, use
    :mod:`physicslab.electricity.Resistivity.from_sheet_resistance` method.
"""

import enum

import numpy as np
import pandas as pd
from scipy.optimize import newton as scipy_optimize_newton

import physicslab.utility


def process(measurement):
    """ Bundle method.

    Parameter :attr:`data` must include `geometry` column. Then either
    `voltage` and `current` or `resistance`. See :class:`Measurement`
    for details and column names.

    :param measurement: Measured data
    :type measurement: pandas.DataFrame
    :return: Sheet resistance
    :rtype: float
    """
    measurement = Measurement(measurement)
    if measurement.resistance_isnull():
        measurement.find_resistances()
    Rh, Rv = measurement.group_and_average()
    return measurement.solve_for_sheet_resistance(Rh, Rv)


class Solve:
    """ Van der Pauw formula and means to solve it. """

    @staticmethod
    def implicit_formula(Rs, Rh, Rv):
        """Van der Pauw measurement implicit function.

        | The function reads:
        | :math:`func(R_s) = exp(-\\pi R_v/R_s) + exp(-\\pi R_h/R_s) - 1`.
        | This function's roots give the solution.

        :param Rs: Sheet resistance. Independent variable - MUST be first
        :type Rs: float
        :param Rh: Horizontal resistance
        :type Rh: float
        :param Rv: Vertical resistance
        :type Rv: float
        :return: We choose the coefficients such that return value is zero
        :rtype: float
        """
        return np.exp(-np.pi * Rv / Rs) + np.exp(-np.pi * Rh / Rs) - 1

    @staticmethod
    def solve(Rh, Rv):
        """ Common computation flow.

        :param Rh: Horizontal resistance
        :type Rh: float
        :param Rv: Vertical resistance
        :type Rv: float
        :return: Sheet resistance
        :rtype: float
        """
        Rs0 = Solve.square(Rh, Rv)
        return Solve.universal(Rh, Rv, Rs0)

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
    def universal(Rh, Rv, Rs0):
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

    :param data: Voltage/current pairs or resistances, defaults to None
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
    def get_columns(cls, voltage_current=True, resistance=True):
        """ Columns of :data:`data`.

        Geometry column is always included.

        :param voltage_current: Include voltage and current columns,
            defaults to True
        :type voltage_current: bool, optional
        :param resistance: Include resistance column, defaults to True
        :type resistance: bool, optional
        :return: List of names. Actual names are saved in class variables.
        :rtype: list(str)
        """
        output = [cls.GEOMETRY]
        if voltage_current:
            output.extend([cls.VOLTAGE, cls.CURRENT])
        if resistance:
            output.append(cls.RESISTANCE)
        return output

    def resistance_isnull(self):
        """ Resistance column not exists or isnull.

        :return: Not exists or isnull
        :rtype: bool
        """
        return (self.RESISTANCE not in self.data.columns
                or self.data[self.RESISTANCE].isnull().any())

    def find_resistances(self):
        """ Populate :attr:`data.RESISTANCE` using Ohm's law. """
        self.data.loc[:, self.RESISTANCE] = (
            physicslab.electricity.Resistance.from_ohms_law(
                self.data[self.VOLTAGE], self.data[self.CURRENT])
        )

    def group_and_average(self):
        """ Classify geometries into either :class:`Geometry.Horizontal`
        or :class:`Geometry.Vertical`. Then average respective resistances.

        :return: Horizontal and vertical sheet resistances
        :rtype: tuple(float, float)
        """
        self.data.loc[:, self.GEOMETRY] = self.data[self.GEOMETRY].apply(
            Geometry.classify)
        group = {
            Geometry.RHorizontal: [],
            Geometry.RVertical: [],
        }
        for i, row in self.data.iterrows():
            group[row[self.GEOMETRY]].append(row[self.RESISTANCE])
        Rh = np.average(group[Geometry.RHorizontal])
        Rv = np.average(group[Geometry.RVertical])
        return Rh, Rv

    def solve_for_sheet_resistance(self, Rh, Rv):
        """ Solve :meth:`Solve.implicit_formula` to find sample's
        sheet resistance. Also compute resistance symmetry ratio (how
        squarish the sample is).

        :param Rh: Horizontal resistance
        :type Rh: float
        :param Rv: Vertical resistance
        :type Rv: float
        :return: Sheet resistance and symmetry ratio
        :rtype: tuple(float, float)
        """
        Rs0 = Solve.square(Rh, Rv)
        sheet_resistance = Solve.universal(Rh, Rv, Rs0)

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

    @staticmethod
    def reverse_polarity(geometry):
        """ Reverse polarity of voltage and current.

        :param geometry: Input
        :type geometry: Geometry
        :return: Reversed geometry
        :rtype: Geometry
        """
        old_value = geometry.value
        if len(old_value) == 2:
            return geometry

        new_value = ''.join(
            [old_value[i:i+2][::-1] for i in range(0, len(old_value), 2)]
        )
        return Geometry(new_value)

    @staticmethod
    def shift(geometry, number=1, counterclockwise=True):
        """ Shift used measuring pins counterclockwise.

        :param geometry: Input
        :type geometry: Geometry
        :param number: Number of pins to jump. Must be between -4 and 4,
            defaults to 1
        :type number: int, optional
        :param counterclockwise: Direction of rotation, defaults to True
        :type counterclockwise: bool, optional
        :raises AttributeError: If parameter :attr:`number` is not
            between -4 and 4
        :return: Rotated geometry
        :rtype: Geometry
        """
        old_value = geometry.value

        if number > np.abs(len(old_value)):
            raise AttributeError(
                'Parameter "number" must be between -4 and 4!')
        if not counterclockwise:
            number *= -1

        new_value = old_value[-number:] + old_value[:-number]
        return Geometry(new_value)

    def _permutation_sign(self):
        """
        :return: Permutation sign of :data:`self.value`.
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
        :type geometry: Geometry
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
        :rtype: Geometry
        """
        if isinstance(geometry, Geometry):
            return Geometry._classify(geometry)

        elif isinstance(geometry, pd.Series):
            return geometry.apply(Geometry._classify)

        else:
            raise NotImplemented
