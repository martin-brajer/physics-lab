"""
Electricity related properties.

Mainly mutual conversion and units.
"""


from scipy.constants import e as elementary_charge


class Carrier_concentration:
    """ Number of charge carriers in per unit volume.

    Also known as Charge carrier density.
    """

    #: SI unit.
    UNIT = '1/m^3'

    @staticmethod
    def from_sheet_density(sheet_density, thickness):
        """ Find carrier concentration from sheet density.

        :param float sheet_density: (1/m^2)
        :param float thickness: (m)
        :return: (1/m^3)
        :rtype: float
        """
        return sheet_density / thickness


class Carrier_sheet_concentration:
    """ Number of charge carriers in per unit area.

    Also known as Charge carrier sheet density.
    """

    #: SI unit.
    UNIT = '1/m^2'


class Mobility:
    """ Electrical mobility is the ability of charged particles (such as
    electrons or holes) to move through a medium in response to an electric
    field that is pulling them.
    """

    #: SI unit.
    UNIT = 'm^2/V/s'

    @staticmethod
    def from_sheets(sheet_density, sheet_resistance):
        """ Find mobility from sheet density and sheet resistance

        :param float sheet_density: (1/m^2)
        :param float sheet_resistance: (ohms per square)
        :return: (m^2/V/s)
        :rtype: float
        """
        return 1 / elementary_charge / sheet_density / sheet_resistance


class Resistance:
    """ Object property. """

    #: SI unit.
    UNIT = 'ohm'

    @staticmethod
    def from_ohms_law(voltage, current):
        """ Find resistivity from sheet resistance.

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
        :return: (ohm metre)
        :rtype: float
        """
        return resistivity / cross_sectional_area * length


class Conductance:
    """ Object property. """

    #: SI unit. Also "siemens"
    UNIT = '1/ohm'

    @staticmethod
    def from_resistance(resistance):
        """ Find conductance from resistance.

        :param float resistance: (ohm)
        :return: (1/ohm)
        :rtype: float
        """
        return 1 / resistance


class Sheet_Resistance:
    """ Thin object property. """

    #: SI unit.
    UNIT = 'ohms per square'

    @staticmethod
    def from_resistivity(resistivity, thickness):
        """Find sheet resistance from resistivity.

        :param float resistivity: (ohm m)
        :param float thickness: (m)
        :return: (ohms per square)
        :rtype: float
        """
        return resistivity / thickness


class Sheet_Conductance:
    """ Thin object property. """

    #: SI unit. Also "siemens square"
    UNIT = '1/ohms square'

    @staticmethod
    def from_sheet_resistance(sheet_resistance):
        return 1 / sheet_resistance


class Resistivity:
    """ Material property. """

    #: SI unit.
    UNIT = 'ohm m'

    @staticmethod
    def from_sheet_resistance(sheet_resistance, thickness):
        """ Find resistivity from sheet resistance.

        :param float sheet_resistance: (ohms per square)
        :param float thickness: (m)
        :return: (ohm m)
        :rtype: float
        """
        return sheet_resistance * thickness

    @staticmethod
    def from_resistance(resistance,  cross_sectional_area, length):
        """ Find resistivity from resistance.

        :param float resistance: (ohm)
        :param float cross_sectional_area: (m^2)
        :param float length: (m)
        :return: (ohm m)
        :rtype: float
        """
        return resistance * cross_sectional_area / length


class Conductivity:
    """ Material property. """

    #: SI unit. Also "siemens/metre"
    UNIT = '1/ohm/m'

    @staticmethod
    def from_resistivity(resistivity):
        """ Find conductivity from resistivity.

        :param float resistivity: (ohm m)
        :return: (1/ohm/m)
        :rtype: float
        """
        return 1 / resistivity
