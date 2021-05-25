"""
Electricity related properties.

Mainly mutual conversion and units.
"""


from scipy.constants import e as elementary_charge


def carrier_concentration(sheet_density, thickness):
    """ Number of charge carriers in per unit volume.

    Also known as Charge carrier density.

    UNIT = '1/m^3'
    """

    return sheet_density / thickness


class Mobility:
    """ Electrical mobility is the ability of charged particles (such as
    electrons or holes) to move through a medium in response to an electric
    field that is pulling them.
    """

    UNIT = 'm^2/V/s'

    @staticmethod
    def from_sheets(sheet_density, sheet_resistance):
        return 1 / elementary_charge / sheet_density / sheet_resistance


class Resistance:
    """ Object property. """

    #: SI unit.
    UNIT = 'ohm'

    @staticmethod
    def from_ohms_law(voltage, current):
        """Find resistivity from sheet resistance.

        :param float voltage: (volt)
        :param float current: (ampere)
        :return: (ohm)
        :rtype: float
        """
        return voltage / current

    @staticmethod
    def from_resistivity(resistivity,  cross_sectional_area, length):
        """ Find resistivity from resistance.

        :param float resistance: (ohm)
        :param float cross_sectional_area: (meter squared)
        :param float length: (meter)
        :return: (ohm-metre)
        :rtype: float
        """
        return resistivity / cross_sectional_area * length


class Sheet_Resistance:
    """ Thin object property. """

    #: SI unit.
    UNIT = 'ohms per square'

    @staticmethod
    def from_resistivity(resistivity, thickness):
        """Find sheet resistance from resistivity.

        :param float resistivity: (ohm-meter)
        :param float thickness: (meter)
        :return: (ohms per square)
        :rtype: float
        """
        return resistivity / thickness


class Resistivity:
    """ Material property. """

    #: SI unit.
    UNIT = 'ohm-meter'

    @staticmethod
    def from_sheet_resistance(sheet_resistance, thickness):
        """Find resistivity from sheet resistance.

        :param float sheet_resistance: (ohms per square)
        :param float thickness: (meter)
        :return: (ohm-metre)
        :rtype: float
        """
        return sheet_resistance * thickness

    @staticmethod
    def from_resistance(resistance,  cross_sectional_area, length):
        """ Find resistivity from resistance.

        :param float resistance: (ohm)
        :param float cross_sectional_area: (meter squared)
        :param float length: (meter)
        :return: (ohm-metre)
        :rtype: float
        """
        return resistance * cross_sectional_area / length
