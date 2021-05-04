"""
Magnetization measurement.


"""


import numpy as np
import pandas as pd

from scipy.optimize import curve_fit as scipy_optimize_curve_fit

from physicslab.curves import magnetic_hysteresis_loop


#: Column names used in :meth:`process` function.
PROCESS_COLUMNS = [
    'magnetic_susceptibility',
    'offset',
    'saturation',
    'remanence',
    'coercivity',
    'ratio_DM_FM',
]


def process(data):
    """ Bundle method.

    Parameter :attr:`data` must include magnetic field and
    magnetization and/or temperature. See :class:`Measurement` for
    details and column names.

    :param pandas.DataFrame data: Measured data
    :return: Derived quantities listed in :data:`PROCESS_COLUMNS`.
    :rtype: pandas.Series
    """
    measurement = Measurement(data)

    magnetic_susceptibility, offset = measurement.diamagnetism(
        from_residual=True)
    saturation, remanence, coercivity = measurement.ferromagnetism(
        from_residual=True)
    ratio_DM_FM = abs(
        measurement.data[Measurement.Columns.DIAMAGNETISM].iloc[-1]
        / measurement.data[Measurement.Columns.FERROMAGNETISM].iloc[-1])

    return pd.Series(
        data=(magnetic_susceptibility, offset, saturation, remanence,
              coercivity, ratio_DM_FM),
        index=PROCESS_COLUMNS)


class Measurement():
    """ Magnetization measurement.

    Copy magnetization column as :data:`Columns.RESIDUAL_MAGNETIZATION`,
    so individual magnetic effects can be subtracted.

    :param pandas.DataFrame data: Magnetic field, magnetization and temperature
        data. See :class:`Measurement.Columns` for default column names.
    """

    class Columns:
        """ :data:`data` column names. """
        #:
        MAGNETICFIELD = 'B'
        #:
        MAGNETIZATION = 'M'
        #: :data:`data` residue column name suffix.
        RESIDUAL_MAGNETIZATION = 'M_residual'
        #:
        FERROMAGNETISM = 'Ferromagnetism'
        #: Simulated data (fit).
        DIAMAGNETISM = 'Diamagnetism'

    def __init__(self, data):
        self.data = data
        self.reset_residue()

    def reset_residue(self):
        """ Place a copy :data:`Columns.MAGNETIZATION` to
        :data:`Columns.RESIDUAL_MAGNETIZATION` column of :data:`data`. """
        self.data[self.Columns.RESIDUAL_MAGNETIZATION] = \
            self.data[self.Columns.MAGNETIZATION].copy()

    def diamagnetism(self, from_residual=False):
        """ Find diamagnetic component of overall magnetization.

        Simulated data are subtracted from residue column.

        :param from_residual: Use residual data instead of the original data,
            defaults to False
        :type from_residual: bool, optional
        :return: Magnetic susceptibility and magnetization offset
        :rtype: tuple
        """
        magnetization_label = (self.Columns.RESIDUAL_MAGNETIZATION
                               if from_residual
                               else self.Columns.MAGNETIZATION)
        coef = self._lateral_linear_fit(self.data[self.Columns.MAGNETICFIELD],
                                        self.data[magnetization_label])
        offset, magnetic_susceptibility = coef

        # Simulate data.
        fit = np.polynomial.polynomial.polyval(
            self.data[self.Columns.MAGNETICFIELD], coef)
        self.data[self.Columns.DIAMAGNETISM] = fit

        self.data.loc[:, self.Columns.RESIDUAL_MAGNETIZATION] -= fit
        return magnetic_susceptibility, offset

    @staticmethod
    def _lateral_linear_fit(x, y, percentage=10):
        """ Linear fit bypassing central region (there can be hysteresis loop).

        Separate fit of top and bottom part. Then average.

        :param numpy.ndarray x: Free variable
        :param numpy.ndarray y: Function value
        :param percentage: How far from either side should the fitting go.
            Using value, because center can be measured with higher
            accuracy, defaults to 10
        :type percentage: int, optional
        :return: Array of fitting parameters sorted in ascending order.
        :rtype: numpy.ndarray
        """
        lateral_interval = (max(x) - min(x)) * percentage / 100

        mask = x >= max(x) - lateral_interval
        popt_top = np.polynomial.polynomial.polyfit(x[mask], y[mask], 1)

        mask = x <= min(x) + lateral_interval
        popt_bottom = np.polynomial.polynomial.polyfit(x[mask], y[mask], 1)

        return (popt_bottom + popt_top) / 2  # Two-element array.

    def ferromagnetism(self, from_residual=False, p0=None):
        """ Find ferromagnetic component of overall magnetization.

        Simulated data are subtracted from residue column.
        Hysteresis loop shape can be found in
        :meth:`physicslab.curves.magnetic_hysteresis_loop`.

        :param from_residual: Use residual data instead of the original data,
            defaults to False
        :type from_residual: bool, optional
        :param p0: Initial guess of parameters. If None, the parameters will
            be estimated automatically, defaults to None
        :type p0: tuple, optional
        :return: Saturation, remanence and coercivity
        :rtype: tuple
        """
        magnetization_label = (self.Columns.RESIDUAL_MAGNETIZATION
                               if from_residual
                               else self.Columns.MAGNETIZATION)
        if p0 is None:
            p0 = self._ferromagnetism_parameter_guess(magnetization_label)
        popt, pcov = scipy_optimize_curve_fit(
            f=magnetic_hysteresis_loop,
            xdata=self.data[self.Columns.MAGNETICFIELD],
            ydata=self.data[magnetization_label],
            p0=p0
        )
        saturation, remanence, coercivity = popt

        # Simulate data.
        fit = magnetic_hysteresis_loop(
            self.data[self.Columns.MAGNETICFIELD], *popt)
        self.data[self.Columns.FERROMAGNETISM] = fit
        self.data.loc[:, self.Columns.RESIDUAL_MAGNETIZATION] -= fit

        return saturation, remanence, coercivity

    def _ferromagnetism_parameter_guess(self, magnetization_label):
        """ Try to guess ferromagnetic hysteresis loop parameters.

        :param str magnetization_label: Source magnetization column name
        :return: saturation, remanence, coercivity
        :rtype: tuple
        """
        magnetic_field = self.data[self.Columns.MAGNETICFIELD]
        magnetization = self.data[magnetization_label]

        saturation = abs(max(magnetization) - min(magnetization)) / 2
        remanence = saturation / 2
        coercivity = abs(max(magnetic_field) - min(magnetic_field)) / 10

        return saturation, remanence, coercivity
