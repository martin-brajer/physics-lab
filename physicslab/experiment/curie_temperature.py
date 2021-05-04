"""
Curie temperature.


"""


import numpy as np
import pandas as pd

from scipy.optimize import curve_fit as scipy_optimize_curve_fit

from physicslab.curves import spontaneous_magnetization


#: Column names used in :meth:`process` function.
PROCESS_COLUMNS = [
    'curie_temperature',
]


def process(data):
    """ Bundle method.

    Parameter :attr:`data` must include temperature and magnetization.
    See :class:`Measurement` for details and column names.

    :param data: Measured data
    :type data: pandas.DataFrame
    :return: Derived quantities listed in :data:`PROCESS_COLUMNS`.
    :rtype: pandas.Series
    """
    measurement = Measurement(data)
    TC = measurement.analyze()

    return pd.Series(
        data=(TC,),
        index=PROCESS_COLUMNS)


class Measurement():
    """ Magnetization vs temperature measurement.

    :param pandas.DataFrame data: Magnetic field, magnetization and
        temperature data. See :class:`Measurement.Columns` for default column
        names.
    """

    class Columns:
        """ :data:`data` column names. """
        #:
        TEMPERATURE = 'T'
        #:
        MAGNETIZATION = 'M'
        #:
        HIGHTEMPERATUREFIT = 'high_temperature_fit'

    def __init__(self, data):
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
        TC, fit = self.fit(
            T=self.data[self.Columns.TEMPERATURE],
            M=self.data[self.Columns.MAGNETIZATION],
            p0=p0,
            high_temperature_focus=True
        )

        self.data[self.Columns.HIGHTEMPERATUREFIT] = fit
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
        :return: TC(second parameter), fit
        :rtype: tuple(float, numpy.ndarray)
        """
        p0 = self._parameter_guess(T, M)
        sigma = 1 / T**2 if high_temperature_focus else None
        popt, pcov = scipy_optimize_curve_fit(
            f=spontaneous_magnetization, xdata=T, ydata=M, p0=p0, sigma=sigma)

        TC = popt[1]
        fit = spontaneous_magnetization(T, *popt)
        return TC, fit

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
