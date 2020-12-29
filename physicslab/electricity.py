"""
Electricity
"""
# __all__ =


class Resistance:
    """ Object property.

    SI unit: ohm
    """

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


class Sheet_Resistance:
    """ Thin object property.

    """

    #: SI unit.
    UNIT = 'ohms per square'

    pass


class Resistivity:
    """ Material property.

    SI unit: ohm-meter
    """

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
