"""
Modules for particular experiments and general functions.
"""


from types import ModuleType
from typing import Union

import pandas as pd

from . import curie_temperature
from . import hall
from . import magnetism_type
from . import profilometer
from . import sem
from . import van_der_pauw


#: :attr:`pandas.Dataframe.attrs` tag.
UNITS = 'units'


def process(data_list: list, by_module: ModuleType, **kwargs) -> pd.DataFrame:
    """ Genereal process function calling appropriate :func:`process` function
    from selected :mod:`experiment` module.

    Include units attribute.

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
    results = []
    for i, data in enumerate(data_list):
        series = by_module.process(data, **kwargs)
        series.name = data.name if hasattr(data, 'name') else i
        results.append(series)

    df = pd.DataFrame(results)
    df.attrs[UNITS] = by_module.process(None)
    return df


def print(df: Union[pd.DataFrame, pd.Series]) -> None:
    """ Print the data including units row if available.

    | Does not change the input DataFrame.
    | If :class:`~pandas.Series` is supplied, it's printed in the
        :class:`~pandas.DataFrame` format.

    :param df: Data to be printed
    :type df: pandas.DataFrame or pandas.Series
    """
    # :attr:`pandas.Dataframe.attrs` is experimental. See:
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.attrs.html
    if df.attrs and UNITS in df.attrs:
        units = df.attrs[UNITS]
    else:
        units = None
    
    if isinstance(df, pd.Series):  # Must be after units readout.
        df = pd.DataFrame(df).transpose()

    if units is not None:
        df_units = pd.DataFrame(units).transpose()  # Make it a row.
        df = pd.concat([df_units, df], axis=0)  # Should do hard copy.

    print(df)
