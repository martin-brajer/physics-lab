"""
Curves
"""
# __all__ =


import numpy as np


def gaussian_curve(x, expected_value, variance, amplitude=None, zero=0):
    """ Gauss curve function of given parameters.

    :param numpy.ndarray x: Free variable
    :param float expected_value: Center
    :param float variance: Variance (not FWHM)
    :param amplitude: Amplitude (value at maximum relative to
        the baseline). None normalize as probability, defaults to None
    :type amplitude: float, optional
    :param int zero: Baseline, defaults to 0
    :return: Gaussian curve values
    :rtype: numpy.ndarray
    """
    if amplitude is None:
        amplitude = 1 / (variance * np.sqrt(2 * np.pi))
    return zero + amplitude * np.exp(
        -((x - expected_value)**2) / (2 * variance**2))


def gaussian_curve_FWHM(variance):
    return 2 * np.sqrt(2 * np.ln(2)) * variance


def spontaneous_magnetization(T, M0, TC, a, b, zero):
    """ An empirical interpolation of the low temperature and the critical
    temperature regimes.

    :param numpy.ndarray T: Temperature
    :param float M0: Spontaneous magnetization at absolute zero
    :param float TC: Curie temperature
    :param float a: Magnetization stays close to :attr:`M0` at higher
        temperatures
    :param float b: Critical exponent. Magnetization stays close to
        :attr:`zero` lower below :attr:`TC`
    :param float zero: Baseline
    :return: Magnetization
    :rtype: numpy.ndarray
    """
    M = np.zeros_like(T)
    mask = T < TC
    M[mask] = M0 * (1 - (T[mask] / TC) ** a) ** b
    return zero + M


def magnetic_hysteresis_branch(H, saturation, remanence, coercivity,
                               rising_branch=True):
    """ One branch of magnetic hysteresis loop.

    :param numpy.ndarray H: external magnetic field strength.
    :param float saturation: :math:`max(B)`
    :param float remanence: :math:`B(H=0)`
    :param float coercivity: :math:`H(B=0)`
    :param rising_branch: Rising (True) or falling (False) branch,
        defaults to True
    :type rising_branch: bool, optional
    :raises ValueError: If saturation is negative or zero
    :raises ValueError: If remanence is negative
    :raises ValueError: If coercivity is negative
    :raises ValueError: If remanence is greater than saturation
    :return: Resulting magnetic field induction :math:`B`
    :rtype: numpy.ndarray
    """
    if saturation <= 0:
        raise ValueError('Saturation must be positive.')
    if remanence < 0:
        raise ValueError('Remanence must be positive or zero.')
    if coercivity < 0:
        raise ValueError('Coercivity must be positive or zero.')
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

    :param numpy.ndarray H: external magnetic field strength. The array
        is split in half for individual branches.
    :param float saturation: :math:`max(B)`
    :param float remanence: :math:`B(H=0)`
    :param float coercivity: :math:`H(B=0)`
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

    Call the instance to enumerate it at the given `x`.
    You can do arithmetic with :class:`Line`, find zeros, etc.

    :param constant: Constant term (:math:`a_0`), defaults to 0
    :type constant: int, optional
    :param slope: Linear term (:math:`a_1`), defaults to 0
    :type slope: int, optional
    """

    def __init__(self, constant=0, slope=0):
        self.constant = constant
        self.slope = slope

    def __call__(self, x):
        """ Find function values of self.

        :param numpy.ndarray x: Free variable
        :return: Function value
        :rtype: numpy.ndarray
        """
        return self.slope * x + self.constant

    def zero(self):
        """ Find free variable (`x`) value which evaluates to zero.

        :raises ValueError: If slope is zero.
        """
        if self.slope == 0:
            raise ValueError('Constant function cannot be inverted.')
        return -self.constant / self.slope

    def root(self):
        """ Alias for :meth:`zero`. """
        return self.zero()

    def invert(self):
        """ Return inverse function of self.

        :return: Inverted function
        :rtype: Line
        """
        return Line(
            constant=self.zero(),  # Raises error if self.slope == 0.
            slope=1 / self.slope
        )

    @staticmethod
    def Intersection(line1, line2):
        """ Find intersection coordinates of the two given :class:`Line`.

        :param Line line1: First line
        :param Line line2: Second line
        :return: Coordinates of the intersection of the two lines
        :rtype: tuple
        """
        x = (line1 - line2).zero()
        return (x, line1(x))

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
