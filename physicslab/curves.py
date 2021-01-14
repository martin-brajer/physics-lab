"""
Curves
"""
# __all__ =


import numpy as np


def gaussian_curve(amplitude, variance, expectedValue, zero):
    """ Create gauss curve function of given parameters.

    :param float amplitude: Amplitude (value at maximum relative to
        the baseline)
    :param float variance: Variance (not FWHM)
    :param float expectedValue: Center
    :param float zero: Baseline
    :return: Gaussian curve as a function of one free variable
    :rtype: function(:class:`numpy.ndarray`)
    """
    return lambda x: amplitude * np.exp(
        -((x - expectedValue)**2) / (2 * variance**2)) + zero


def magnetic_hysteresis_branch(H, saturation, remanence, coercivity,
                               rising_branch=True):
    """ One branch of magnetic hysteresis loop.

    :param H: external magnetic field strength.
    :type H: numpy.ndarray
    :param saturation: :math:`max(B)`
    :type saturation: float
    :param remanence: :math:`B(H=0)`
    :type remanence: float
    :param coercivity: :math:`H(B=0)`
    :type coercivity: float
    :param rising_branch: Rising (True) or falling (False) branch,
        defaults to True
    :type rising_branch: bool, optional
    :raises ValueError: If saturation is not positive
    :raises ValueError: If remanence is not positive
    :raises ValueError: If coercivity is not positive
    :raises ValueError: If remanence is greater than saturation
    :return: Resulting magnetic field induction :math:`B`
    :rtype: numpy.ndarray
    """
    if saturation <= 0:
        raise ValueError('Saturation must be positive.')
    if remanence <= 0:
        raise ValueError('Remanence must be positive.')
    if coercivity <= 0:
        raise ValueError('Coercivity must be positive.')
    if remanence >= saturation:
        raise ValueError('Remanence must be less than saturation.')

    const = np.arctanh(remanence / saturation) / coercivity
    coercivity_sign = 1 if rising_branch else -1

    B = saturation * np.tanh(const * (H - (coercivity_sign * coercivity)))
    return B


def magnetic_hysteresis_loop(H, saturation, remanence, coercivity):
    """ Magnetic hysteresis loop.

    If more control is needed, use :func:`magnetic_hysteresis_branch`.
    To check whether the data starts with rising or falling part,
    first and middle element are compared.

    :param H: external magnetic field strength. The array is split in half
        for individual branches.
    :type H: numpy.ndarray
    :param saturation: :math:`max(B)`
    :type saturation: float
    :param remanence: :math:`B(H=0)`
    :type remanence: float
    :param coercivity: :math:`H(B=0)`
    :type coercivity: float
    :return: Resulting magnetic field induction :math:`B`
    :rtype: numpy.ndarray
    """
    # Starting high => falling first.
    falling_first = H[0] > H[int(len(H) / 2)]

    H_rising, H_falling = np.array_split(H, 2)
    if falling_first:
        H_falling, H_rising = H_rising, H_falling

    B_rising = magnetic_hysteresis_branch(
        H_rising, saturation, remanence, coercivity, rising_branch=True)
    B_falling = magnetic_hysteresis_branch(
        H_falling, saturation, remanence, coercivity, rising_branch=False)

    if falling_first:
        B_falling, B_rising = B_rising, B_falling
    return np.append(B_rising, B_falling)


class Line():
    """ Represents a line function: :math:`y=a_0+a_1x`.

    :param constant: Constant term (:math:`a_0`), defaults to 0
    :type constant: int, optional
    :param slope: Linear term (:math:`a_1`), defaults to 0
    :type slope: int, optional
    """

    def __init__(self, constant=0, slope=0):
        self.constant = constant
        self.slope = slope

    def invert(self):
        """ Return inverse function of self.

        :return: Inverted function
        :rtype: :class:`Line`
        """
        return Line(
            constant=-self.constant / self.slope,
            slope=1 / self.slope
        )

    @staticmethod
    def Intersection(line1, line2):
        """ Return coordinates of intersection point of
        the two :class:`Line` instances.

        :param line1: First line
        :type line1: :class:`Line`
        :param line2: Second line
        :type line2: :class:`Line`
        :return: Coordinates of the intersection of the two lines
        :rtype: tuple
        """
        x = ((line1.constant - line2.constant)
             / (line2.slope - line1.slope))
        return (x, line1(x))

    def __call__(self, x):
        """ Find function values of self.

        :param x: Free variable
        :type x: :class:`numpy.ndarray`
        :return: Function value
        :rtype: :class:`numpy.ndarray`
        """
        return self.slope * x + self.constant

    def __add__(self, value):
        if isinstance(value, Line):
            constant = self.constant + value.constant
            slope = self.slope + value.slope
        else:
            constant = self.constant + value
            slope = self.slope
        return Line(constant, slope)

    def __sub__(self, value):
        return self + (-value)

    def __mul__(self, value):
        constant = self.constant * value
        slope = self.slope * value
        return Line(constant, slope)

    def __truediv__(self, value):
        return self * (1 / value)

    def __pos__(self):
        return self

    def __neg__(self):
        return Line(-self.constant, -self.slope)

    def __eq__(self, value):
        return self.constant == value.constant and self.slope == value.slope

    def __ne__(self, value):
        return not (self == value)

    def __bool__(self):
        return self != Line(0, 0)

    def __str__(self):
        return 'Line: y = {constant} {slope_sign} {slope_abs}x'.format(
            constant=self.constant,
            slope_sign='+' if self.slope >= 0 else '-',
            slope_abs=np.abs(self.slope)
        )

    def __repr__(self):
        return 'Line(constant={constant}, slope={slope})'.format(
            constant=self.constant, slope=self.slope)

    def __radd__(self, value):
        return self + value

    def __rsub__(self, value):
        return -(self - value)

    def __rmul__(self, value):
        return self * value
