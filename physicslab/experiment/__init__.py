"""
Modules for particular experiments.
"""


import pandas as pd

from physicslab.experiment import van_der_pauw
from physicslab.experiment import hall


def process(measurements, by_module, **kwargs):
    output = pd.DataFrame(columns=by_module.PROCESS_COLUMNS)
    for name, data in measurements:
        series = by_module.process(data, **kwargs)
        series.name = name
        output = output.append(series)
    return output
