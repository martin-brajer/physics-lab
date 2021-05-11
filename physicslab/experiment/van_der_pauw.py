""" Van der Pauw resistivity measurement.

| Four-point measurement bypass resistance of ohmic contacts.
| To find resistivity from sheet resistance, use
    :mod:`physicslab.electricity.Resistivity.from_sheet_resistance` method.
| Pay special attention to enum :class:`Geometry`.
"""

import enum

import numpy as np
import pandas as pd
from scipy.optimize import newton as scipy_optimize_newton

from physicslab.utility import permutation_sign
from physicslab.electricity import Resistivity, Resistance


#: Column names used in :meth:`process` function.
PROCESS_COLUMNS = [
    'sheet_resistance',
    'ratio_resistance',
    'sheet_conductance',
    'resistivity',
    'conductivity',
]


def process(data, thickness=None):
    """ Bundle method.

    Parameter :attr:`data` must include `geometry` column. Then either
    `voltage` and `current` or `resistance`. See :class:`Measurement`
    for details and column names.

    The optional parameter allows to calculate additional quantities:
    `resistivity` and `conductivity`.

    :param data: Measured data
    :type data: pandas.DataFrame
    :param thickness: Sample dimension perpendicular to the plane marked
        by the electrical contacts, defaults to None
    :type thickness: float, optional
    :return: Derived quantities listed in :data:`PROCESS_COLUMNS`.
    :rtype: pandas.Series
    """
    measurement = Measurement(data)
    (resistivity, conductivity) = [np.nan] * 2

    measurement.find_resistances()
    Rh, Rv = measurement.group_geometries_and_average()
    sheet_resistance, ratio_resistance = measurement.analyze(Rh, Rv)
    sheet_conductance = 1 / sheet_resistance
    if thickness is not None:
        resistivity = Resistivity.from_sheet_resistance(
            sheet_resistance, thickness)
        conductivity = sheet_conductance / thickness

    return pd.Series(
        data=(sheet_resistance, ratio_resistance, sheet_conductance,
              resistivity, conductivity),
        index=PROCESS_COLUMNS)


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
        :return: Quantification of this formula is meant to be zero
        :rtype: float
        """
        return np.exp(-np.pi * Rv / Rs) + np.exp(-np.pi * Rh / Rs) - 1

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

        Universal formula. Computation flow for square-like samples is
        as follows:

        .. code:: python

            Rs0 = van_der_pauw.Solve.Square(Rh, Rv)
            Rs = van_der_pauw.Solve.universal(Rh, Rv, Rs0)

        :param Rh: Horizontal resistance
        :type Rh: float
        :param Rv: Vertical resistance
        :type Rv: float
        :param Rs0: Approximate value to start with.
        :type Rs0: float
        :return: Sheet resistance
        :rtype: float
        """
        return scipy_optimize_newton(
            Solve.implicit_formula, Rs0, args=(Rh, Rv), fprime=None)


class Measurement:
    """ Van der Pauw resistances measurements.

    :param pandas.DataFrame data: Voltage/current pairs or resistances with
        respective geometries. See :class:`Measurement.Columns` for default
        column names.
    """

    class Columns:
        """ :data:`data` column names. """
        #:
        GEOMETRY = 'Geometry'
        #:
        VOLTAGE = 'Voltage'
        #:
        CURRENT = 'Current'
        #:
        RESISTANCE = 'Resistance'

    def __init__(self, data):
        self.data = data

    def find_resistances(self):
        """ Populate :attr:`data.RESISTANCE` using Ohm's law. """
        self.data.loc[:, self.Columns.RESISTANCE] = Resistance.from_ohms_law(
            self.data[self.Columns.VOLTAGE], self.data[self.Columns.CURRENT])

    def group_geometries_and_average(self):
        """ Classify geometries into either :class:`Geometry.Horizontal`
        or :class:`Geometry.Vertical`. Then average respective resistances.

        :return: Horizontal and vertical sheet resistances
        :rtype: tuple(float, float)
        """
        self.data.loc[:, self.Columns.GEOMETRY] = (
            self.data[self.Columns.GEOMETRY].apply(Geometry.classify))
        group = {
            Geometry.RHorizontal: [],
            Geometry.RVertical: [],
        }
        for i, row in self.data.iterrows():
            group[row[self.Columns.GEOMETRY]].append(
                row[self.Columns.RESISTANCE])
        Rh = np.average(group[Geometry.RHorizontal])
        Rv = np.average(group[Geometry.RVertical])
        return Rh, Rv

    def analyze(self, Rh, Rv):
        """ Solve :meth:`Solve.implicit_formula` to find sample's
        sheet resistance. Also compute resistance symmetry ratio (always
        greater than one). The ratio shows how squarish the sample is,
        quality of ohmic contacts (small, symmetric etc.).

        :param Rh: Horizontal resistance
        :type Rh: float
        :param Rv: Vertical resistance
        :type Rv: float
        :return: Sheet resistance and symmetry ratio
        :rtype: tuple(float, float)
        """
        Rs0 = Solve.square(Rh, Rv)
        sheet_resistance = Solve.universal(Rh, Rv, Rs0)

        ratio_resistance = Rh / Rv
        if ratio_resistance < 1:
            ratio_resistance = 1 / ratio_resistance

        return sheet_resistance, ratio_resistance


class Geometry(enum.Enum):
    """ Resistance measurement configurations :class:`enum.Enum`.

    Legend: ``Rijkl`` = :math:`R_{ij,kl} = V_{kl}/I_{ij}`. The contacts are
    numbered from 1 to 4 in a counter-clockwise order, beginning at the
    top-left contact. See `Van der Pauw method
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

    def reverse_polarity(self):
        """ Reverse polarity of voltage and current.

        :return: Reversed geometry
        :rtype: Geometry
        """
        if len(self.value) == 2:
            return self

        # len(self.value) == 4
        new_value = ''.join(  # self.value[pairs][reverse order]
            [self.value[i:i+2][::-1] for i in range(0, len(self.value), 2)]
        )
        return Geometry(new_value)

    def shift(self, number=1, counterclockwise=True):
        """ Shift measuring pins counterclockwise.

        :param number: Number of pins to jump, defaults to 1
        :type number: int, optional
        :param counterclockwise: Direction of rotation, defaults to True
        :type counterclockwise: bool, optional
        :return: Rotated geometry
        :rtype: Geometry
        """
        number = number % len(self.value)
        if not counterclockwise:
            number *= -1

        new_value = self.value[-number:] + self.value[:-number]
        return Geometry(new_value)

    def is_horizontal(self):
        """ Find whether the geometry describes horizontal configuration.

        :return: Is horizontal?
        :rtype: bool
        """
        return permutation_sign(self.value) == -1

    def is_vertical(self):
        """ Find whether the geometry describes vertical configuration.

        :return: Is vertical?
        :rtype: bool
        """
        return permutation_sign(self.value) == 1

    @staticmethod
    def _classify(geometry):
        """ Sort given :class:`Geometry` to either vertical or horizontal
        group.

        :param geometry: Geometry to evaluate
        :type geometry: Geometry
        :return: One of the two main configurations
        :rtype: Geometry
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
            raise NotImplementedError()
