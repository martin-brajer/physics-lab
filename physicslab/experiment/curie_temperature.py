"""
Curie temperature.

Find Curie temperature from magnetization vs temperature measurement.
"""


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scipy.optimize import curve_fit

from physicslab.curves import spontaneous_magnetization
from physicslab.utility import _ColumnsBase, get_name


def process(data):
    """ Bundle method.

    Parameter :attr:`data` must include temperature and magnetization.
    See :class:`Columns` for details and column names.

    Supplying `None` for :attr:`data` returns :class:`pandas.Series` of
    the same columns with values being units.

    :param data: Measured data. If None, return units instead
    :type data: pandas.DataFrame
    :return: Derived quantities listed in :meth:`Columns.process` or units
    :rtype: pandas.Series
    """
    if data is None:
        from physicslab.experiment import UNITS
        name = UNITS
        curie_temperature = 'K'

    else:
        name = get_name(data)
        measurement = Measurement(data)

        curie_temperature = measurement.analyze()

    return pd.Series(
        data=(curie_temperature,),
        index=Columns.process(), name=name)


class Columns(_ColumnsBase):
    """ Bases: :class:`physicslab.utility._ColumnsBase`

    Column names.
    """
    TEMPERATURE = 'T'
    MAGNETIZATION = 'M'
    HIGH_TEMPERATURE_FIT = 'high_temperature_fit'
    CURIE_TEMPERATURE = 'curie_temperature'

    @classmethod
    def mandatory(cls):
        """ Get the current values of the mandatory column names.

        :rtype: set(str)
        """
        return {cls.TEMPERATURE, cls.MAGNETIZATION}

    @classmethod
    def process(cls):
        """ Get the current values of the :func:`process` output column names.

        :rtype: lits(str)
        """
        return [cls.CURIE_TEMPERATURE]


class Measurement():
    """ Magnetization vs temperature measurement.

    :param pandas.DataFrame data: Magnetization and temperature data.
    :raises ValueError: If :attr:`data` is missing a mandatory column
    """

    def __init__(self, data):
        if not Columns.mandatory().issubset(data.columns):
            raise ValueError('Missing mandatory column. See Columns class.')
        self.data = data

    def analyze(self, p0=None):
        """ Find Curie temperature.

        :param p0: Initial guess of spontaneous magnetization curve parameters.
            If None, the parameters will be estimated automatically,
            defaults to None
        :type p0: tuple, optional
        :return: Curie temperature
        :rtype: float
        """
        TC, fit_data = self.fit(
            T=self.data[Columns.TEMPERATURE],
            M=self.data[Columns.MAGNETIZATION],
            p0=p0,
            high_temperature_focus=True
        )

        self.data[Columns.HIGH_TEMPERATURE_FIT] = fit_data
        return TC

    def fit(self, T, M, p0=None, high_temperature_focus=False):
        """ Fit spontaneous magnetization curve to the data.

        Save the fit into :data:`Columns.HIGHTEMPERATUREFIT`.

        :param numpy.ndarray T: Temperature
        :param numpy.ndarray M: Magnetization
        :param p0: Initial guess of spontaneous magnetization curve parameters.
            If None, the parameters will be estimated automatically,
            defaults to None
        :type p0: tuple, optional
        :param high_temperature_focus: Give high temperature data more weight,
            defaults to False
        :type high_temperature_focus: bool, optional
        :return: Curie temperature, fit
        :rtype: tuple(float, numpy.ndarray)
        """
        p0 = self._parameter_guess(T, M)
        sigma = 1 / T**2 if high_temperature_focus else None
        popt, pcov = curve_fit(
            f=spontaneous_magnetization, xdata=T, ydata=M, p0=p0, sigma=sigma)

        TC = popt[1]
        fit_data = spontaneous_magnetization(T, *popt)
        return TC, fit_data

    def _parameter_guess(self, T, M):
        """ Try to guess :meth:`physicslab.curves.spontaneous_magnetization`
        parameters.

        :param numpy.ndarray T: Temperature
        :param numpy.ndarray M: Magnetization
        :return: M0, TC, a, b, zero
        :rtype: tuple
        """
        M0 = max(M)
        TC = 0.9 * max(T)  # At 90 %.
        a = 4
        b = 0.6
        zero = min(M)
        return M0, TC, a, b, zero


def plot(data_list):
    """ Simple plot data and fit for all measurement at once.

    :param data_list:
    :type data_list: list[pandas.DataFrame]
    :return: Same objects as from :meth:`matplotlib.pyplot.subplots`
    :rtype: tuple[~matplotlib.figure.Figure, ~matplotlib.axes.Axes]
    """
    fig, ax = plt.subplots(num='Curie temperature')
    ax.set_title('Focus on high temperature part while fitting')
    for data in data_list:
        T = data[Columns.TEMPERATURE]

        ax.plot(T, data[Columns.MAGNETIZATION], 'ko')
        ax.plot(T, data[Columns.HIGH_TEMPERATURE_FIT], 'r-')

    ax.set_xlabel('Temperature / K')
    ax.set_ylabel('Magnetization / emu')

    return fig, ax
