"""
Modules for particular experiments.
"""


import physicslab.experiment.van_der_pauw
import physicslab.experiment.hall


def process(measurements, by_module, **kwargs):
    output = by_module.process(None)
    for name, data in measurements:
        series = by_module.process(data, **kwargs)
        series.name = name
        output = output.append(series)
    return output
