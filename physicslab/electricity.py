"""
Electricity
"""
# __all__ =


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

        :param voltage: (volt)
        :type voltage: float
        :param current: (ampere)
        :type current: float
        :return: (ohm)
        :rtype: float
        """
        return voltage / current

    @staticmethod
    def from_resistivity(resistivity,  cross_sectional_area, length):
        """ Find resistivity from resistance.

        :param resistance: (ohm)
        :type resistance: float
        :param cross_sectional_area: (meter squared)
        :type cross_sectional_area: float
        :param length: (meter)
        :type length: float
        :return: (ohm-metre)
        :rtype: float
        """
        return resistivity / cross_sectional_area * length


class Sheet_Resistance:
    """ Thin object property. """

    #: SI unit.
    UNIT = 'ohms per square'

    pass


class Resistivity:
    """ Material property. """

    #: SI unit.
    UNIT = 'ohm-meter'

    @staticmethod
    def from_sheet_resistance(sheet_resistance, thickness):
        """Find resistivity from sheet resistance.

        :param sheet_resistance: (ohms per square)
        :type sheet_resistance: float
        :param thickness: (meter)
        :type thickness: float
        :return: (ohm-metre)
        :rtype: float
        """
        return sheet_resistance * thickness

    @staticmethod
    def from_resistance(resistance,  cross_sectional_area, length):
        """ Find resistivity from resistance.

        :param resistance: (ohm)
        :type resistance: float
        :param cross_sectional_area: (meter squared)
        :type cross_sectional_area: float
        :param length: (meter)
        :type length: float
        :return: (ohm-metre)
        :rtype: float
        """
        return resistance * cross_sectional_area / length
