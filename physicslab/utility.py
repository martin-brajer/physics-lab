"""
Utility functions
"""
# __all__ =


import numpy as np
import pandas as pd


def permutation_sign(array):
    """ Computes permutation sign of given array.

    Relative to ordered array, see: :math:`sgn(\\sigma) =
    (-1)^{\\sum_{0 \\le i<j<n}(\\sigma_i>\\sigma_j)}`

    .. note::
        For permutation relative to another ordering, use the
        following identity:
        :math:`sgn(\\pi_1 \\circ \\pi_2) = sgn(\\pi_1)\\cdot sgn(\\pi_2)`

    :param array: Input array (iterable)
    :type array: list
    :return: Permutation parity sign is either (+1) or (-1)
    :rtype: int
    """
    number_of_inversions = 0
    n = len(array)
    for i in range(n):
        for j in range(i + 1, n):
            if array[i] > array[j]:
                number_of_inversions += 1
    return (-1) ** number_of_inversions


def squarificate(iterable, filler=None):
    """ Reshape 1D :attr:`iterable` into squarish 2D array.

    Mainly use with :meth:`physicslab.ui.plot_grid`, if the positions
    are arbitrary.

    Example: reshape :class:`list` of 10 elements into 3x4 array.
    The two new elements will be populated by :attr:`filler`.

    :param iterable: Source 1D iterable. E.g. list of filenames
    :type iterable: list, numpy.ndarray
    :param filler: Value to pad the array with, defaults to None
    :type filler: object, optional
    :return: Modified array
    :rtype: numpy.ndarray
    """
    if isinstance(iterable, np.ndarray):  # Numpy
        array = iterable
    if isinstance(iterable, (pd.Series, pd.DataFrame)):  # Pandas
        array = iterable.values
    else:
        array = np.array(iterable)  # Other (list, tuple)

    num = array.shape
    if len(num) > 1:
        raise ValueError('iterable attribute must be 1D')
    num = num[0]
    ncols = int(np.ceil(np.sqrt(num)))  # Width. Round up to int.
    nrows = int(np.ceil(num / ncols))  # Height.
    missing = nrows * ncols - num

    array = np.pad(array, (0, missing), mode='constant',
                   constant_values=filler)
    array = array.reshape((nrows, ncols))
    return array
