"""
Magnetization measurement.

Separate diamagnetic and ferromagnetic contributions.
"""


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scipy.optimize import curve_fit as scipy_optimize_curve_fit

from physicslab.curves import magnetic_hysteresis_loop
from physicslab.utility import _ColumnsBase, get_name


def process(data, diamagnetism=True, ferromagnetism=True):
    """ Bundle method.

    Parameter :attr:`data` must include magnetic field and magnetization.
    See :class:`Columns` for details and column names.

    Output :attr:`ratio_DM_FM` compares max values - probably for the
    strongest magnetic field.

    :param pandas.DataFrame data: Measured data
    :param diamagnetism: Look for diamagnetism contribution, defaults to True
    :type diamagnetism: bool, optional
    :param ferromagnetism: Look for ferromagnetism contribution,
        defaults to True
    :type ferromagnetism: bool, optional
    :return: Derived quantities listed in :meth:`Columns.output`.
    :rtype: pandas.Series
    """
    measurement = Measurement(data)
    (magnetic_susceptibility, offset, saturation, remanence,
     coercivity, ratio_DM_FM) = [np.nan] * 6

    if diamagnetism:
        magnetic_susceptibility, offset = measurement.diamagnetism(
            from_residual=True)
    if ferromagnetism:
        saturation, remanence, coercivity = measurement.ferromagnetism(
            from_residual=True)
    if diamagnetism and ferromagnetism:
        ratio_DM_FM = abs(measurement.data[Columns.DIAMAGNETISM].iloc[-1]
                          / measurement.data[Columns.FERROMAGNETISM].iloc[-1])

    return pd.Series(
        data=(magnetic_susceptibility, offset, saturation, remanence,
              coercivity, ratio_DM_FM),
        index=Columns.output(), name=get_name(data))


class Columns(_ColumnsBase):
    """ Bases: :class:`physicslab.utility._ColumnsBase`

    Column names.
    """
    MAGNETICFIELD = 'B'
    MAGNETIZATION = 'M'
    # :data:`data` residue after DM/FM component subtraction.
    RESIDUAL_MAGNETIZATION = 'M_residual'
    FERROMAGNETISM = 'Ferromagnetism'
    DIAMAGNETISM = 'Diamagnetism'
    MAGNETIC_SUSCEPTIBILITY = 'magnetic_susceptibility'
    OFFSET = 'offset'
    SATURATION = 'saturation'
    REMANENCE = 'remanence'
    COERCIVITY = 'coercivity'
    RATIO_DM_FM = 'ratio_DM_FM'

    @classmethod
    def mandatory(cls):
        """ Get the current mandatory column names.

        :rtype: set(str)
        """
        return {cls.MAGNETICFIELD, cls.MAGNETIZATION}

    @classmethod
    def output(cls):
        """ Get the current values of the :func:`process` output column names.

        :rtype: lits(str)
        """
        return [cls.MAGNETIC_SUSCEPTIBILITY, cls.OFFSET, cls.SATURATION,
                cls.REMANENCE, cls.COERCIVITY, cls.RATIO_DM_FM]


class Measurement():
    """ Magnetization vs magnetic field measurement.

    Copy magnetization column as :data:`Columns.RESIDUAL_MAGNETIZATION`,
    so individual magnetic effects can be subtracted.

    :param pandas.DataFrame data: Magnetic field and magnetization data.
    :raises ValueError: If :attr:`data` is missing a mandatory column
    """

    def __init__(self, data):
        if not Columns.mandatory().issubset(data.columns):
            raise ValueError('Missing mandatory column. See Columns class.')
        self.data = data
        self.data[Columns.RESIDUAL_MAGNETIZATION] = \
            self.data[Columns.MAGNETIZATION].copy()

    def _magnetization_label(self, from_residual):
        if from_residual:
            return Columns.RESIDUAL_MAGNETIZATION
        else:
            return Columns.MAGNETIZATION

    def diamagnetism(self, from_residual=False):
        """ Find diamagnetic component of overall magnetization.

        Simulated data are subtracted from residue column (making it centred).

        :param from_residual: Use residual data instead of the original data,
            defaults to False
        :type from_residual: bool, optional
        :return: Magnetic susceptibility and magnetization offset
        :rtype: tuple
        """
        coef = self._lateral_linear_fit(
            self.data[Columns.MAGNETICFIELD],
            self.data[self._magnetization_label(from_residual)]
        )

        fit = np.polynomial.polynomial.polyval(
            self.data[Columns.MAGNETICFIELD], coef)
        self.data[Columns.DIAMAGNETISM] = fit
        self.data.loc[:, Columns.RESIDUAL_MAGNETIZATION] -= fit

        offset, magnetic_susceptibility = coef
        return magnetic_susceptibility, offset

    @staticmethod
    def _lateral_linear_fit(x, y, percentage=10):
        """ Linear fit bypassing central region (there can be hysteresis loop).

        Separate fit of top and bottom part. Then average.

        :param numpy.ndarray x: Free variable
        :param numpy.ndarray y: Function value
        :param percentage: How far from either side should the fitting go.
            Using value, because center can be measured with higher accuracy,
            defaults to 10
        :type percentage: int, optional
        :return: Array of fitting parameters sorted in ascending order.
        :rtype: numpy.ndarray
        """
        lateral_interval = (max(x) - min(x)) * percentage / 100

        mask = x >= max(x) - lateral_interval
        popt_top = np.polynomial.polynomial.polyfit(x[mask], y[mask], 1)

        mask = x <= min(x) + lateral_interval
        popt_bottom = np.polynomial.polynomial.polyfit(x[mask], y[mask], 1)

        # Two-element array (const, slope).
        return (popt_bottom + popt_top) / 2

    def ferromagnetism(self, from_residual=False, p0=None):
        """ Find ferromagnetic component of overall magnetization.

        | Simulated data are subtracted from residue column.
        | Hysteresis loop shape can be found in
            :meth:`~physicslab.curves.magnetic_hysteresis_loop`.

        :param from_residual: Use residual data instead of the original data,
            defaults to False
        :type from_residual: bool, optional
        :param p0: Initial guess of hysteresis loop parameters. If None, the
            parameters will be estimated automatically, defaults to None
        :type p0: tuple, optional
        :return: Saturation, remanence and coercivity
        :rtype: tuple
        """
        magnetization = self.data[self._magnetization_label(from_residual)]
        if p0 is None:
            p0 = self._ferromagnetism_parameter_guess(
                B=self.data[Columns.MAGNETICFIELD], M=magnetization)
        popt, pcov = scipy_optimize_curve_fit(
            f=magnetic_hysteresis_loop,
            xdata=self.data[Columns.MAGNETICFIELD],
            ydata=magnetization,
            p0=p0
        )
        saturation, remanence, coercivity = popt

        fit = magnetic_hysteresis_loop(
            self.data[Columns.MAGNETICFIELD], *popt)
        self.data[Columns.FERROMAGNETISM] = fit
        self.data.loc[:, Columns.RESIDUAL_MAGNETIZATION] -= fit

        return saturation, remanence, coercivity

    @staticmethod
    def _ferromagnetism_parameter_guess(B, M):
        """ Try to guess ferromagnetic hysteresis loop parameters.

        :param float B: Magnetic field
        :param float M: Magnetization
        :return: Saturation, remanence, coercivity
        :rtype: tuple
        """
        saturation = abs(max(M) - min(M)) * 0.5  # 50 %
        remanence = saturation * 0.5  # 25 %
        coercivity = abs(max(B) - min(B)) * 0.1  # 10 %

        return saturation, remanence, coercivity


def plot(data):
    """ Plot single magnetization measurement separated data

    :param data:
    :type data: list[pandas.DataFrame]
    """
    plt.figure('Magnetism type')
    B = data[Columns.MAGNETICFIELD]

    plt.plot(B, data[Columns.MAGNETIZATION], 'ko', label='Data')
    plt.plot(B, data[Columns.DIAMAGNETISM], 'r-', label='Diamagnetism')
    plt.plot(B, data[Columns.FERROMAGNETISM], 'b-', label='Ferromagnetism')
    plt.plot(B, data[Columns.RESIDUAL_MAGNETIZATION], 'g-', label='Residue')

    plt.legend()
