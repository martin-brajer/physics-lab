"""
Van der Pauw resistivity measurement.

| Four-point measurement bypass resistance of ohmic contacts.
| To find resistivity from sheet resistance, use
    :mod:`physicslab.electricity.Resistivity.from_sheet_resistance` method.
| Pay special attention to enum :class:`Geometry`.
"""


import enum

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import newton as scipy_optimize_newton

from physicslab.electricity import Resistivity, Resistance
from physicslab.ui import plot_grid
from physicslab.utility import (_ColumnsBase, permutation_sign,
                                squarificate, get_name)


def process(data, thickness=None):
    """ Bundle method.

    Parameter :attr:`data` must include geometry voltage and current.
    See :class:`Columns` for details and column names.

    The optional parameter allows to calculate additional quantities:
    `resistivity` and `conductivity`.

    :param data: Measured data
    :type data: pandas.DataFrame
    :param thickness: Sample dimension perpendicular to the plane marked
        by the electrical contacts, defaults to None
    :type thickness: float, optional
    :return: Derived quantities listed in :meth:`Columns.output`.
    :rtype: pandas.Series
    """
    measurement = Measurement(data)
    (resistivity, conductivity) = [np.nan] * 2

    Rh, Rv = measurement.analyze()
    sheet_resistance, ratio_resistance = Solve.analyze(Rh, Rv)
    sheet_conductance = 1 / sheet_resistance
    if thickness is not None:
        resistivity = Resistivity.from_sheet_resistance(sheet_resistance,
                                                        thickness)
        conductivity = 1 / resistivity

    return pd.Series(
        data=(sheet_resistance, ratio_resistance, sheet_conductance,
              resistivity, conductivity),
        index=Columns.output(), name=get_name(data))


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

    @classmethod
    def universal(cls, Rh, Rv, Rs0):
        """ Compute sheet resistance from the given resistances.

        Universal formula. Computation flow for square-like samples is
        as follows:

        .. code:: python

            Rs0 = van_der_pauw.Solve.square(Rh, Rv)
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
            cls.implicit_formula, Rs0, args=(Rh, Rv), fprime=None)

    @classmethod
    def analyze(cls, Rh, Rv):
        """ Solve :meth:`Solve.implicit_formula` to find sample's
        sheet resistance. Also compute resistance symmetry ratio (always
        greater than one). The ratio assess how squarish the sample is,
        quality of ohmic contacts (small, symmetric) etc.

        :param Rh: Horizontal resistance
        :type Rh: float
        :param Rv: Vertical resistance
        :type Rv: float
        :return: Sheet resistance and symmetry ratio
        :rtype: tuple(float, float)
        """
        Rs0 = cls.square(Rh, Rv)
        sheet_resistance = cls.universal(Rh, Rv, Rs0)

        ratio_resistance = Rh / Rv
        if ratio_resistance < 1:
            ratio_resistance = 1 / ratio_resistance

        return sheet_resistance, ratio_resistance


class Columns(_ColumnsBase):
    """ Bases: :class:`physicslab.utility._ColumnsBase`

    Column names.
    """
    GEOMETRY = 'Geometry'
    VOLTAGE = 'Voltage'
    CURRENT = 'Current'
    RESISTANCE = 'Hall_resistance'
    SHEET_RESISTANCE = 'sheet_resistance'
    RATIO_RESISTANCE = 'ratio_resistance'
    SHEET_CONDUCTANCE = 'sheet_conductance'
    RESISTIVITY = 'resistivity'
    CONDUCTIVITY = 'conductivity'

    @classmethod
    def mandatory(cls):
        """ Get the current mandatory column names.

            :rtype: set(str)
            """
        return {cls.GEOMETRY, cls.VOLTAGE, cls.CURRENT}

    @classmethod
    def output(cls):
        """ Get the current values of the :func:`process` output column names.

        :rtype: lits(str)
        """
        return [cls.SHEET_RESISTANCE, cls.RATIO_RESISTANCE,
                cls.SHEET_CONDUCTANCE, cls.RESISTIVITY, cls.CONDUCTIVITY]


class Measurement:
    """ Van der Pauw resistances measurements.

    :param pandas.DataFrame data: Voltage-current pairs with respective
        geometries.
    :raises ValueError: If :attr:`data` is missing a mandatory column
    """

    def __init__(self, data):
        if not Columns.mandatory().issubset(data.columns):
            raise ValueError('Missing mandatory column. See Columns class.')
        self.data = data

    def analyze(self):
        """ Classify geometries into either :attr:`Geometry.Horizontal`
        or :attr:`Geometry.Vertical`. Then average respective hall resistances.

        Additionally save Hall resistances to :data:`data`.

        :return: Horizontal and vertical sheet resistances
        :rtype: tuple(float, float)
        """
        self.data.loc[:, Columns.RESISTANCE] = Resistance.from_ohms_law(
            self.data[Columns.VOLTAGE], self.data[Columns.CURRENT])

        geometries = self.data[Columns.GEOMETRY].apply(Geometry.classify)
        mask = geometries.apply(Geometry.is_horizontal)
        Rh = self.data.loc[mask, Columns.RESISTANCE].mean()
        Rv = self.data.loc[~mask, Columns.RESISTANCE].mean()
        return Rh, Rv


class Geometry(enum.Enum):
    """ Resistance measurement configuration :class:`~enum.Enum`.

    Legend: ``Rijkl`` = :math:`R_{ij,kl} = V_{kl}/I_{ij}`. The contacts are
    numbered from 1 to 4 in a counter-clockwise order beginning at the
    top-left contact. See `Van der Pauw method
    <https://en.wikipedia.org/wiki/Van_der_Pauw_method#Reversed_polarity_measurements>`_
    at Wikipedia.
    There are two additional group values: ``Vertical`` and ``Horizontal``.
    """
    R1234 = '1234'
    R3412 = '3412'
    R2143 = '2143'
    R4321 = '4321'

    R2341 = '2341'
    R4123 = '4123'
    R3214 = '3214'
    R1432 = '1432'

    Vertical = '12'
    Horizontal = '21'

    def reverse_polarity(self):
        """ Reverse polarity of voltage and current.

        :return: Reversed geometry
        :rtype: Geometry
        """
        if len(self.value) == 2:
            return self

        # len(self.value) == 4
        new_value = ''.join(  # [self.value[pairs][reverse order] for ...]
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

    def classify(self):
        """ Sort the Geometry to either vertical or horizontal group.

        :return: One of the two group configurations
        :rtype: Geometry
        """
        if self.is_horizontal():
            return self.Horizontal
        else:
            return self.Vertical


def plot(data_list, output):
    """ Plot individual measurements and results with quality coefficients.

    For plotting details, see:
    https://matplotlib.org/stable/tutorials/intermediate/gridspec.html#a-complex-nested-gridspec-using-subplotspec

    :param data_list:
    :type data_list: list[pandas.DataFrame]
    :param output: Analysis data from :func:`physicslab.experiment.process`
    :type output: pandas.DataFrame
    """
    df = pd.DataFrame(data=squarificate(data_list))
    title = 'Van der Pauw'

    # Plotting initialization.
    size = mpl.rcParams['figure.figsize']
    size = (size[0] * 2, size[1])  # Double width.
    fig = plt.figure(num=title, figsize=size)
    outer_grid = fig.add_gridspec(1, 2)

    # Grid plot.
    inner_grid = outer_grid[0].subgridspec(*df.shape)
    axs_grid = inner_grid.subplots()

    def plot_value(ax, value: pd.DataFrame):
        for ori in value['ori'].drop_duplicates():
            value_ori = value.loc[value['ori'] == ori, :]
            ax.plot(value_ori[Columns.VOLTAGE],
                    value_ori[Columns.CURRENT], 'o-')
    plot_grid(df, plot_value, fig_axs=(fig, axs_grid), title=title,
              ylabel='Current', row_labels=False, column_labels=False)
    fig.text(0.30, 0.04, 'Voltage', ha='center')

    # Single plot.
    ax_plot = fig.add_subplot(outer_grid[1])
    ax_plot.plot(output[Columns.SHEET_CONDUCTANCE], 'ko:')
    ax_plot.set_xlabel('Measurement number')
    ax_plot.set_ylabel('Sheet conductance [$(k\\Omega)^{-1}$]')
    ax_plot.set_ylim(bottom=0)

    color = 'red'
    ax_plot_2 = ax_plot.twinx()
    ax_plot_2.plot(output[Columns.RATIO_RESISTANCE], 'o:', c=color)
    ax_plot_2.set_ylabel('$R_{12} / R_{23}$ {>1}')
    ax_plot_2.spines['right'].set_color(color)
    ax_plot_2.yaxis.label.set_color(color)
    ax_plot_2.tick_params(axis='y', colors=color)
    ax_plot_2.set_ylim(bottom=0)
