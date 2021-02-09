Main
----

.. automodule:: physicslab.experiment
   :members:

.. code:: python

   ### Example: Van der pauw
   import panda as pd

   def load(filename):
      measurement = pd.read_csv(filename)
      measurement.name = filename
      return measurement
   
   thickness = 1.262e-6  # meters
   samples = ['sample#1', 'sample#2', ...]
   measurements = [load(sample) for sample in samples]
   
   results = physicslab.experiment.process(
      measurements,
      by_module=physicslab.experiment.van_der_pauw,
      thickness=thickness
   )
   print(results)

.. code:: bash

              sheet_resistance  ratio_resistance  sheet_conductance  resistivity  conductivity
   sample#1       1.590823e+05          1.168956       6.286055e-06     0.200762      4.981026
   sample#2       1.583278e+05          1.185031       6.316009e-06     0.199810      5.004762
   ...
