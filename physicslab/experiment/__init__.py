"""
Modules for particular experiments and general functions.
"""


import pandas as pd

from physicslab.experiment import curie_temperature
from physicslab.experiment import hall
from physicslab.experiment import magnetism_type
from physicslab.experiment import profilometer
from physicslab.experiment import van_der_pauw


def process(data_list, by_module, **kwargs):
    """ Genereal process function calling appropriate :func:`process` function
    from selected :mod:`experiment` module.

    :param data_list: List of measurements, which are passed to the
        appropriate :func:`process` function
    :type data_list: list(pandas.DataFrame)
    :param by_module: Submodule of :mod:`experiment` by which the individual
        measurements are to be processed
    :type by_module: :mod:`experiment` submodule
    :param kwargs: Additional keyword arguments are forwarded to
        :func:`by_module.process` function
    :return: Collection of results indexed by measurement's :attr:`name`
    :rtype: pandas.DataFrame
    """
    output = []
    for i, data in enumerate(data_list):
        series = by_module.process(data, **kwargs)
        series.name = data.name if hasattr(data, 'name') else i
        output.append(series)
    return pd.DataFrame(output)
