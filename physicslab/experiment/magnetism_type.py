""" Magnetization measurement.

Separate diamagnetic and ferromagnetic contributions.
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


def process(data, diamagnetism=True, ferromagnetism=True):
    """ Bundle method.

    Parameter :attr:`data` must include magnetic field and magnetization.
    See :class:`Measurement` for details and column names.

    Output :attr:`ratio_DM_FM` compares max values - probably for the
    strongest magnetic field.

    :param pandas.DataFrame data: Measured data
    :param diamagnetism: Look for diamagnetism contribution, defaults to True
    :type diamagnetism: bool, optional
    :param ferromagnetism: Look for ferromagnetism contribution,
        defaults to True
    :type ferromagnetism: bool, optional
    :return: Derived quantities listed in :data:`PROCESS_COLUMNS`.
    :rtype: pandas.Series
    """
    measurement = Measurement(data)
    (magnetic_susceptibility, offset, saturation, remanence,
     coercivity, ratio_DM_FM) = [np.nan] * 7

    if diamagnetism:
        magnetic_susceptibility, offset = measurement.diamagnetism(
            from_residual=True)
    if ferromagnetism:
        saturation, remanence, coercivity = measurement.ferromagnetism(
            from_residual=True)
    if diamagnetism and ferromagnetism:
        ratio_DM_FM = abs(
            measurement.data[Measurement.Columns.DIAMAGNETISM].iloc[-1]
            / measurement.data[Measurement.Columns.FERROMAGNETISM].iloc[-1])

    return pd.Series(
        data=(magnetic_susceptibility, offset, saturation, remanence,
              coercivity, ratio_DM_FM),
        index=PROCESS_COLUMNS)


class Measurement():
    """ Magnetization vs magnetic field measurement.

    Copy magnetization column as :data:`Columns.RESIDUAL_MAGNETIZATION`,
    so individual magnetic effects can be subtracted.

    :param pandas.DataFrame data: Magnetic field and magnetization data.
    :raises ValueError: If :attr:`data` is missing a mandatory column
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

        @classmethod
        def mandatory(cls):
            """ Get the current mandatory column names.

            :rtype: set(str)
            """
            return {cls.MAGNETICFIELD, cls.MAGNETIZATION}

    def __init__(self, data):
        if not self.Columns.mandatory().issubset(data.columns):
            raise ValueError('Missing mandatory column. See Columns class.')
        self.data = data
        self.reset_residue()

    def reset_residue(self):
        """ Place a copy :data:`Columns.MAGNETIZATION` to
        :data:`Columns.RESIDUAL_MAGNETIZATION` column of :data:`data`. """
        self.data[self.Columns.RESIDUAL_MAGNETIZATION] = \
            self.data[self.Columns.MAGNETIZATION].copy()

    def _magnetization_label(self, from_residual):
        if from_residual:
            return self.Columns.RESIDUAL_MAGNETIZATION
        else:
            return self.Columns.MAGNETIZATION

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
            self.data[self.Columns.MAGNETICFIELD],
            self.data[self._magnetization_label(from_residual)]
        )

        fit = np.polynomial.polynomial.polyval(
            self.data[self.Columns.MAGNETICFIELD], coef)
        self.data[self.Columns.DIAMAGNETISM] = fit
        self.data.loc[:, self.Columns.RESIDUAL_MAGNETIZATION] -= fit

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
                B=self.data[self.Columns.MAGNETICFIELD], M=magnetization)
        popt, pcov = scipy_optimize_curve_fit(
            f=magnetic_hysteresis_loop,
            xdata=self.data[self.Columns.MAGNETICFIELD],
            ydata=magnetization,
            p0=p0
        )
        saturation, remanence, coercivity = popt

        fit = magnetic_hysteresis_loop(
            self.data[self.Columns.MAGNETICFIELD], *popt)
        self.data[self.Columns.FERROMAGNETISM] = fit
        self.data.loc[:, self.Columns.RESIDUAL_MAGNETIZATION] -= fit

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
