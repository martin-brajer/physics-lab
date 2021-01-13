"""
Magnetization measurement.


"""


import numpy as np
import pandas as pd

from scipy.optimize import newton as scipy_optimize_newton
from scipy.optimize import curve_fit as scipy_optimize_curve_fit

from physicslab.curves import magnetic_hysteresis_loop
from physicslab.electricity import carrier_concentration, Mobility, Resistance


#: Column names used in :meth:`process` function.
PROCESS_COLUMNS = [
    'chi',
    'offset',
    'saturation',
    'remanence',
    'coercivity',
]


def process(data):
    """ Bundle method.

    Parameter :attr:`data` must include voltage/current/magnetic field
    triples. See :class:`Measurement` for details and column names.

    The optional parameters allows to calculate additional quantities:
    `concentration` and `mobility`.

    :param data: Measured data
    :type data: pandas.DataFrame
    :return: Derived quantities listed in :data:`PROCESS_COLUMNS`.
    :rtype: pandas.Series
    """
    measurement = Measurement(data)

    chi, offset = measurement.diamagnetism(from_residual=True)
    saturation, remanence, coercivity = measurement.ferromagnetism(
        from_residual=True)

    return pd.Series(
        data=(chi, offset, saturation, remanence, coercivity),
        index=PROCESS_COLUMNS)


class Measurement():
    """ Magnetization measurement.

    Copy data columns, so individual magnetic effects can be
    subtracted. Work with :meth:`get_columns` columns. Text to add to
    the column names, defaults to '_backup'

    :param data: Voltage/current/magnetic field triples. See class
        variables for default column names.
    :type data: pandas.DataFrame
    :raises AttributeError: If :attr:`data` doesn't include
        :meth:`get_columns` columns.
    """

    #: :data:`data` magnetic field column name of type :class:`float`.
    MAGNETICFIELD = 'B'
    #: :data:`data` magnetization column name of type :class:`float`.
    MAGNETIZATION = 'M'
    #: :data:`data` temperature column name of type :class:`float`.
    TEMPERATURE = 'T'
    #: :data:`data` residue column name suffix of type :class:`float`.
    RESIDUE_SUFFIX = '_residue'

    def __init__(self, data):
        if all(column in data.columns for column in Measurement.get_columns(
                magnetization=False, temperature=False)):
            self.data = data
        else:
            raise AttributeError(
                ':attr:`data` must include {} columns.'.format(
                    self.get_columns(self.MAGNETICFIELD)))

        self._add_residual(self.MAGNETIZATION)

    @classmethod
    def get_columns(cls, magnetization=True, temperature=True):
        """ Columns of :data:`data`.

        Magnetic field column is always included.
        RESIDUE_SUFFIX is never included.

        :param magnetization: Include magnetization column, defaults to True
        :type magnetization: bool, optional
        :param temperature: Include temperature column, defaults to True
        :type temperature: bool, optional
        :return: List of names. Actual names are saved in class variables.
        :rtype: list(str)
        """
        output = [cls.MAGNETICFIELD]
        if magnetization:
            output.append(cls.MAGNETIZATION)
        if temperature:
            output.append(cls.TEMPERATURE)
        return output

    def _add_residual(self, column):
        """ Copy a column, so analytical methods can subtract what they found.

        E.g. :meth:`diamagnetism` subtracts diamagnetic contribution to the
        overall magnetization.

        :param column: Column name
        :type column: str
        """
        self.data[column + self.RESIDUE_SUFFIX] = (
            self.data.loc[:, column].copy())

    def diamagnetism(self, from_residual=False,
                     fit_label='Diamagnetism', fit_array=None):
        """ Find diamagnetic component.

        :param subtract: [description], defaults to False
        :type subtract: bool, optional
        :param fit_label: [description], defaults to 'Diamagnetism'
        :type fit_label: str, optional
        :param fit_array: [description], defaults to None
        :type fit_array: [type], optional
        :return: [description]
        :rtype: [type]
        """
        magnetization_label = self._label(self.MAGNETIZATION, from_residual)

        coef = self.lateral_linear_fit(self.data[self.MAGNETICFIELD],
                                       self.data[magnetization_label])
        offset, chi = coef

        # Save fitted curve.
        if fit_label is not None:
            if fit_array is None:
                fit_array = self.data[self.MAGNETICFIELD]
            self.data[fit_label] = np.polynomial.polynomial.polyval(
                fit_array, coef)

        # Modify magnetization residue.
        self._modify_residue(self.MAGNETIZATION,
                             original_data_label=magnetization_label,
                             simulated_data=np.polynomial.polynomial.polyval(
                                 self.data[self.MAGNETICFIELD], coef))

        return chi, offset

    @staticmethod
    def lateral_linear_fit(x, y, percentage=10):
        """ Linear fit bypassing central region (there can be hysteresis loop).

        Separate fit of top and bottom part. Then average.

        :param x: Free variable
        :type x: numpy.ndarray
        :param y: Function value
        :type y: numpy.ndarray
        :param percentage: Using value, because center is
            often measured with higher accuracy, defaults to 10
        :type percentage: int, optional
        :return: Array of fitting parameters beginning by the highest order
        :rtype: numpy.ndarray
        """
        lateral_interval = (max(x) - min(x)) * percentage / 100

        mask = x > max(x) - lateral_interval
        popt_top = np.polynomial.polynomial.polyfit(x[mask], y[mask], 1)

        mask = x < min(x) + lateral_interval
        popt_bottom = np.polynomial.polynomial.polyfit(x[mask], y[mask], 1)

        return (popt_bottom + popt_top) / 2

    def ferromagnetism(self, from_residual=False,
                       fit_label='Ferromagnetism', fit_array=None):
        """[summary]

        :param from_residual: [description], defaults to False
        :type from_residual: bool, optional
        :param fit_label: [description], defaults to 'Ferromagnetism'
        :type fit_label: str, optional
        :param fit_array: [description], defaults to None
        :type fit_array: [type], optional
        :return: [description]
        :rtype: [type]
        """
        magnetization_label = self._label(self.MAGNETIZATION, from_residual)

        p0 = self._ferromagnetism_parmeter_guess(magnetization_label)
        popt, pcov = scipy_optimize_curve_fit(
            f=magnetic_hysteresis_loop,
            xdata=self.data[self.MAGNETICFIELD],
            ydata=self.data[magnetization_label],
            p0=p0
        )
        saturation, remanence, coercivity = popt

        # Save fitted curve.
        if fit_label is not None:
            if fit_array is None:
                fit_array = self.data[self.MAGNETICFIELD]
            self.data[fit_label] = magnetic_hysteresis_loop(
                fit_array, *popt)

        # Modify magnetization residue.
        self._modify_residue(self.MAGNETIZATION,
                             original_data_label=magnetization_label,
                             simulated_data=magnetic_hysteresis_loop(
                                 self.data[self.MAGNETICFIELD], *popt))

        return saturation, remanence, coercivity

    def _ferromagnetism_parmeter_guess(self, magnetization_label):
        magnetization = self.data[magnetization_label]

        saturation = (max(magnetization) - min(magnetization)) / 2
        remanence = 2.2e-3
        coercivity = 600

        return (saturation, remanence, coercivity)

    def _label(self, column, residual):
        if residual:
            column += self.RESIDUE_SUFFIX
        return column

    def _modify_residue(self, column, original_data_label, simulated_data):
        residual_data_label = self._label(column, True)
        original_data = self.data[original_data_label]

        self.data.loc[:, residual_data_label] = original_data - simulated_data
