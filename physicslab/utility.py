"""
Utility functions
"""
# __all__ =


def permutation_sign(arr):
    """ Computes permutation sign of given array.

    Relative to ordered array, see:
    :math:`\\textrm{sgn}(\\sigma) = (-1)^{\\sum_{0 \\le i<j<n}
    (\\sigma_i>\\sigma_j)}`

    :param arr: Input array.
    :type arr: list or :mod:`numpy.array`
    :return: Permutation parity: (+1) or (-1)
    :rtype: int
    """
    counter = 0
    n = len(arr)
    for i in range(n):
        for j in range(i + 1, n):
            if arr[i] > arr[j]:
                counter += 1
    return (-1) ** counter
