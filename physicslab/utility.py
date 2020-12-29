"""
Utility functions
"""
# __all__ =


def permutation_sign(array):
    """ Computes permutation sign of given array.

    Relative to ordered array, see: :math:`sgn(\\sigma) =
    (-1)^{\\sum_{0 \\le i<j<n}(\\sigma_i>\\sigma_j)}`

    .. note::
        For permutation relative to another ordering, use the
        following identity:
        :math:`sgn(\\pi_1 \\circ \\pi_2) = sgn(\\pi_1)\\;sgn(\\pi_2)`

    :param array: Input array.
    :type array: list or :mod:`numpy.array`
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
