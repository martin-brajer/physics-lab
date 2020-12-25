"""
Electricity
"""
# __all__ =


def resistivity(sheet_resistance, thickness):
    """Find resistivity from sheet resistance.

    :param sheet_resistance: (ohms per square)
    :type sheet_resistance: float
    :param thickness: (metres)
    :type thickness: float
    :return: Resistivity (ohms metres)
    :rtype: float
    """
    return sheet_resistance * thickness
