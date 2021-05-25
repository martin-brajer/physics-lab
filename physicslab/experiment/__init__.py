"""
Modules for particular experiments and general functions.
"""


import pandas as pd

from physicslab.experiment import curie_temperature
from physicslab.experiment import hall
from physicslab.experiment import magnetism_type
from physicslab.experiment import profilometer
from physicslab.experiment import van_der_pauw


def process(measurements, by_module, **kwargs):
    """ Genereal process function calling appropriate *process* function
    from selected :mod:`experiment` module.

    :param measurements: List of measurements, which are passed to
        appropriate *process* method
    :type measurements: list(pandas.DataFrame)
    :param by_module: Submodule of :mod:`experiment` by which the individual
        measurements are to be processed
    :type by_module: :mod:`experiment` submodule
    :param kwargs: Additional keyword arguments are forwarded to
        :meth:`by_module.process` method
    :return: Collection of results indexed by measurement's :attr:`name`
    :rtype: pandas.DataFrame
    """
    output = []
    for i, measurement in enumerate(measurements):
        series = by_module.process(measurement, **kwargs)
        series.name = measurement.name if hasattr(measurement, 'name') else i
        output.append(series)
    return pd.DataFrame(data=output, columns=by_module.PROCESS_COLUMNS)
