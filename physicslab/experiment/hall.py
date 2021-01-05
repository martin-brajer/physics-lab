"""
Hall
"""


import numpy as np
import pandas as pd

from scipy.constants import e as elementary_charge

from physicslab.electricity import carrier_concentration, Mobility, Resistance


#: Column names used in :meth:`process` function.
PROCESS_COLUMNS = [
    'sheet_density',
    'conductivity_type',
    'residual',
    'concentration',
    'mobility',
]


def process(data, thickness=None, sheet_resistance=None):
    measurement = Measurement(data)
    (sheet_density, conductivity_type, residual
     ) = measurement.solve_for_sheet_density(full=True)

    concentration = np.nan if thickness is None \
        else carrier_concentration(sheet_density, thickness)
    mobility = np.nan if sheet_resistance is None \
        else Mobility.from_sheets(sheet_density, sheet_resistance)

    return pd.Series(
        data=(sheet_density, conductivity_type, residual,
              concentration, mobility),
        index=PROCESS_COLUMNS)


class Measurement:
    """ Hall measurement.

    :param data: Voltage/current/magnetic field triples, defaults to None
    :type data: pandas.DataFrame, optional
    :raises AttributeError: If :attr:`data` doesn't include
        :meth:`get_columns` columns.
    """

    def __init__(self, data=None):
        #: Measurement data as :class:`pandas.DataFrame`.
        self.data = None

        if all(column in Measurement.get_columns() for column in data.columns):
            self.data = data
        else:
            raise AttributeError(
                ':attr:`data` must include {} columns.'.format(
                    Measurement.get_columns()))

    @staticmethod
    def get_columns():
        return ['B', 'VH', 'I']

    def is_valid(self):
        # Is hall measurement linear enough?
        return True

    @staticmethod
    def _conductivity_type(hall_voltage):
        if hall_voltage > 0:
            return 'p'
        else:
            return 'n'

    def solve_for_sheet_density(self, full=False):
        self.data['hall_resistance'] = Resistance.from_ohms_law(
            self.data['VH'], self.data['I'])
        coefficients_full = np.polynomial.polynomial.polyfit(
            self.data['hall_resistance'], self.data['B'], 1, full=True)
        slope = coefficients_full[0][1]  # Constant is found at [0][0].
        residual = coefficients_full[1][0]

        signed_sheet_density = slope / -elementary_charge
        if full:
            return (abs(signed_sheet_density),
                    Measurement._conductivity_type(signed_sheet_density),
                    residual)
        else:
            return (abs(signed_sheet_density),
                    _conductivity_type(signed_sheet_density))
