"""
Profile measurement.
"""


import numpy as np
import pandas as pd

from scipy.optimize import curve_fit

import physicslab


#: Column names used in :meth:`process` function.
PROCESS_COLUMNS = [
    'expected_values',
    'variances',
    'amplitudes',
    'FWHMs',
    'thickness',
    'histogram',
]


def process(data, **kwargs):
    """ Bundle method.

    Parameter :attr:`data` must include position and height.
    See :class:`Measurement` for details and column names.

    Output `histogram` column (type :class:`~Measurement.Histogram`) stores
    histogram data and fit data.

    :param data: Measured data
    :type data: pandas.DataFrame
    :param kwargs: All additional keyword arguments are passed to the
        :meth:`Measurement.analyze` call.
    :return: Derived quantities listed in :data:`PROCESS_COLUMNS`.
    :rtype: pandas.Series
    """
    measurement = Measurement(data)
    # () = [np.nan] * 0

    (expected_values, variances, amplitudes, FWHMs, thickness, histogram
     ) = measurement.analyze(**kwargs)
    return pd.Series(
        data=(expected_values, variances, amplitudes, FWHMs, thickness,
              histogram),
        index=PROCESS_COLUMNS)


class Measurement():
    """ Profile measurement.

    :param pandas.DataFrame data: Position and height data.
    :raises ValueError: If :attr:`data` is missing a mandatory column
    """

    class Columns:
        """ :data:`data` column names. """
        #:
        POSITION = 'Position'
        #:
        HEIGHT = 'Height'
        #: Height data after background subtraction.
        HEIGHT_SUB = 'Height_sub'
        #:
        BACKGROUND = 'Background'

        @classmethod
        def mandatory(cls):
            """ Get the current mandatory column names.

            :rtype: set(str)
            """
            return {cls.POSITION, cls.HEIGHT}

    class Histogram:
        """ Histogram and fit data. """

        def __init__(self, bin_centers, count, x_fit, y_fit):
            self.bin_centers = bin_centers
            self.count = count
            self.x_fit = x_fit
            self.y_fit = y_fit

    def __init__(self, data):
        if not self.Columns.mandatory().issubset(data.columns):
            raise ValueError('Missing mandatory column. See Columns class.')
        self.data = data

    def analyze(self, zero=0, background_degree=None, edge_values=None):
        """ Analyze

        :param zero: Assumed position of the main peak, defaults to 0
        :type zero: int, optional
        :param background_degree: Degree of polynomial used to subtract
            background. None to disable background subtraction,
            defaults to None
        :type background_degree: int or None, optional
        :param edge_values: Background subtraction will happen inside those
            bounds. None means left half of the positions, defaults to None
        :type edge_values: tuple(float, float), optional
        :return: Expected values, variances, amplitudes, FWHMs, thickness
            and histogram. The last one is of type
            :class:`~Measurement.Histogram`) and store histogram data and
            fit data.
        :rtype: tuple
        """
        position = self.data[self.Columns.POSITION]
        height = self.data[self.Columns.HEIGHT]

        # Background subtraction.
        if background_degree is None:
            background = np.zeros_like(position)
        else:
            if edge_values is None:
                left = min(position)  # right = max(position)
                length = max(position) - left  # length = right - left
                edge_values = (left, left + length / 2)  # (left, half)
            background = self.background(position, height,
                                         background_degree, edge_values)
        height_sub = height - background
        self.data[self.Columns.BACKGROUND] = background
        self.data[self.Columns.HEIGHT_SUB] = height_sub

        # Histogram.
        margin = abs(max(height_sub) - min(height_sub)) * 0.05  # 5 %
        count, bin_edges = np.histogram(
            height_sub, bins=np.linspace(min(height_sub) - margin,
                                         max(height_sub) + margin,
                                         num=len(height_sub) // 50
                                         ))
        bin_centers = (bin_edges[0:-1] + bin_edges[1:]) / 2

        x_fit, y_fit, popt = self._fit_double_gauss(
            x=bin_centers, y=count, zero=zero)
        FWHM_zero = physicslab.curves.gaussian_curve_FWHM(variance=popt[1])
        FWHM_layer = physicslab.curves.gaussian_curve_FWHM(variance=popt[4])
        thickness = popt[3] - popt[0]  # Expected_value difference.
        histogram = self.Histogram(bin_centers, count, x_fit, y_fit)

        return ((popt[0], popt[3]), (popt[1], popt[4]), (popt[2], popt[5]),
                (FWHM_zero, FWHM_layer), thickness, histogram)

    @staticmethod
    def background(pos, height, background_degree, edge_values):
        """ Find best fit given the constrains.

        :param pos: Position
        :type pos: numpy.ndarray
        :param height: Height
        :type height: numpy.ndarray
        :param background_degree: Degree of polynomial used
        :type background_degree: int
        :param edge_values: Background subtraction will happen inside those
            bounds
        :type edge_values: tuple(float, float)
        :return: Background
        :rtype: numpy.ndarray
        """
        edge_indices = [(np.abs(pos - edge_value)).argmin()
                        for edge_value in edge_values]
        masks = ((edge_values[0] <= pos), (pos <= edge_values[1]))
        mask = masks[0] & masks[1]  # Inside `edge_values` interval.

        sigma = np.ones_like(height[mask])  # Soft-fix edge points.
        sigma[[0, -1]] = 0.001
        x_fit = pos[mask]  # Fit only here.
        popt = np.polynomial.polynomial.polyfit(
            x=x_fit, y=height[mask], deg=background_degree)
        y_fit = np.polynomial.polynomial.polyval(x=x_fit, c=popt)

        # Background array construction.
        background = np.zeros_like(pos)
        # The right section is left unchanged (zero).
        # The center section is mainly fit shifted to match the right part.
        background[mask] = y_fit - height[edge_indices[1]]
        # The left part is constant at fit left-right difference. -[1-0]
        background[~masks[0]] = -np.diff(height[edge_indices])[0]

        return background

    def _fit_double_gauss(self, x, y, zero=0):
        x_fit = np.linspace(min(x), max(x), len(x) * 10)
        p0 = self._guess_double_gauss(x, y, zero=zero)
        popt, pcov = curve_fit(self._double_gauss, x, y, p0)
        y_fit = self._double_gauss(x_fit, *popt)
        return x_fit, y_fit, popt

    @ staticmethod
    def _guess_double_gauss(x, y, zero=0):
        epsilon = abs(max(x) - min(x)) / 100
        mask = (zero - epsilon < x) & (x < zero + epsilon)  # eps neighbourhood
        y_cut = y.copy()
        y_cut[mask] = 0  # Cca eq y[~mask].

        expected_value_zero = zero
        expected_value_layer = x[np.argmax(y_cut)]
        variance_zero = epsilon / 10
        variance_layer = epsilon / 2
        amplitude_zero = max(y[mask])
        amplitude_layer = max(y_cut)

        return (expected_value_zero, variance_zero, amplitude_zero,
                expected_value_layer, variance_layer, amplitude_layer)

    @ staticmethod
    def _double_gauss(x, expected_value1, variance1, amplitude1,
                      expected_value2, variance2, amplitude2):
        return(
            physicslab.curves.gaussian_curve(
                x, expected_value1, variance1, amplitude1)
            + physicslab.curves.gaussian_curve(
                x, expected_value2, variance2, amplitude2)
        )
