"""
Hall measurement.

Induced voltage perpendicular to both current and magnetic field.
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
    """ Bundle method.

    Parameter :attr:`data` must include voltage/current/magnetic field
    triples. See :class:`Measurement` for details and column names.

    The optional parameters allows to calculate additional quantities:
    `concentration` and `mobility`.

    :param data: Measured data
    :type data: pandas.DataFrame
    :param thickness: Sample dimension perpendicular to the plane marked
        by the electrical contacts, defaults to None
    :type thickness: float, optional
    :param sheet_resistance: Defaults to None
    :type sheet_resistance: float, optional
    :return: Derived quantities listed in :data:`PROCESS_COLUMNS`.
    :rtype: pandas.Series
    """
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

    :param data: Voltage/current/magnetic field triples. See class
        variables for default column names.
    :type data: pandas.DataFrame
    :raises AttributeError: If :attr:`data` doesn't include
        :meth:`get_columns` columns.
    """

    #: :data:`data` magnetic field column name of type :class:`float`.
    MAGNETICFIELD = 'B'
    #: :data:`data` Hall voltage column name of type :class:`float`.
    HALLVOLTAGE = 'VH'
    #: :data:`data` current column name of type :class:`float`.
    CURRENT = 'I'

    def __init__(self, data):
        if all(column in Measurement.get_columns() for column in data.columns):
            self.data = data
        else:
            raise AttributeError(
                ':attr:`data` must include {} columns.'.format(
                    self.get_columns()))

    @classmethod
    def get_columns(cls):
        """ Columns of :data:`data`.

        :return: List of names. Actual names are saved in class variables.
        :rtype: list(str)
        """
        return [cls.MAGNETICFIELD, cls.HALLVOLTAGE, cls.CURRENT]

    def is_valid(self):
        # Is hall measurement linear enough?
        return True

    @staticmethod
    def _conductivity_type(hall_voltage):
        """ Find conductivity type based on sign of hall voltage.

        :param hall_voltage: Hall voltage
        :type hall_voltage: float
        :return: Either "p" or "n"
        :rtype: str
        """
        if hall_voltage > 0:
            return 'p'
        else:
            return 'n'

    def solve_for_sheet_density(self, full=False):
        """ Compute sheet density and determine conductivity type.

        :param full: Switch determining the nature of the return value. When
            `False` just sheet density and conductivity type are returned.
            When `True`, fit residual is also returned, defaults to False
        :type full: bool, optional
        :return: Sheet density, conductivity type, (fit residual)
        :rtype: tuple
        """
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
