"""
Utility functions.
"""


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

    | Mainly use with :meth:`physicslab.ui.plot_grid`, if the positions are
        arbitrary.
    | Example: reshape :class:`list` of 10 filenames into 3x4 array. The two
        new elements will be populated by :attr:`filler`.

    :param iterable: Source 1D iterable.
    :type iterable: list, numpy.ndarray
    :param filler: Value to pad the array with, defaults to None
    :type filler: object, optional
    :raises NotImplementedError: If :attr:`iterable` is array-like
    :raises ValueError: If :attr:`iterable` has more than one dimension
    :return: Modified array
    :rtype: numpy.ndarray
    """
    if isinstance(iterable, np.ndarray):  # Numpy
        array = iterable
    if isinstance(iterable, (pd.Series, pd.DataFrame)):  # Pandas
        array = iterable.values
    else:  # Other: list, tuple
        # Array constructor tries to unpack the elements to create
        # a multidimensional array, so the following bypasses it.
        array = np.empty(shape=len(iterable), dtype=object)
        array[:] = iterable

    num = array.shape
    if len(num) > 1:
        raise ValueError('Iterable attribute must be one-dimensional.')
    num = num[0]
    ncols = int(np.ceil(np.sqrt(num)))  # Width. Round up to int.
    nrows = int(np.ceil(num / ncols))  # Height.
    missing = nrows * ncols - num

    array = np.pad(array, (0, missing), mode='constant',
                   constant_values=filler)
    array = array.reshape((nrows, ncols))
    return array


def get_name(df):
    """ Find :class:`~pandas.DataFrame` name.

    :param df: Input
    :type df: pandas.DataFrame or pandas.Series
    :return: Name or None if name does not exist
    :rtype: str or None
    """
    return df.name if hasattr(df, 'name') else None


class _ColumnsBase:
    """ Abstract base class for :class:`physicslab.experiment.[Any].Columns`
    classes. """
    @classmethod
    def list_all_names(cls):
        """
        :rtype: list[str]
        """
        return [name for name in dir(cls) if name.isupper()]
