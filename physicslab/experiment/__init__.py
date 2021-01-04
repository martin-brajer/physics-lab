"""
Modules for particular experiments.
"""


from physicslab.experiment import van_der_pauw
from physicslab.experiment import hall


def process(measurements, by_module, **kwargs):
    output = by_module.process(None)
    for name, data in measurements:
        series = by_module.process(data, **kwargs)
        series.name = name
        output = output.append(series)
    return output
