# -*- coding: utf-8 -*-
"""
Testing of :mod:`physicslab`.

.. note::
    Run this script directly to run a :mod:`unittest`.
"""


import os
import re
import unittest

import pandas as pd
import pycodestyle

try:
    import physicslab
except ImportError:  # If run locally.
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    import physicslab


class TestCodeFormat(unittest.TestCase):

    def test_conformance(self):
        """ Test that we conform to PEP-8. """
        style = pycodestyle.StyleGuide()
        path = os.path.abspath(os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'physicslab'
        ))

        files_test = []
        for root, dirs, files in os.walk(path):
            files_test.extend([os.path.join(path, root, f)
                               for f in files if f.endswith(".py")])
        result = style.check_files(files_test)
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")

    def test_version(self):
        """ Test whether :data:`__version__` follows
        `Semantic Versioning 2.0.0 <https://semver.org/>`_.
        """
        #: Pycodestyle - FAQ: Is there a suggested regular expression
        # (RegEx) to check a SemVer string?
        pattern = (
            r'^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0'
            r'|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-'
            r'9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*'
            r'))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)'
            r'*))?$'
        )
        self.assertTrue(re.search(pattern, physicslab.__version__))


class TestGeometryMethods(unittest.TestCase):

    def test_grouping(self):
        for geometry in physicslab.experiment.van_der_pauw.Geometry:
            self.assertTrue(
                geometry.is_vertical() or geometry.is_horizontal()
            )

    def test_shift(self):
        vdp = physicslab.experiment.van_der_pauw
        self.assertEqual(
            vdp.Geometry.R2341,
            vdp.Geometry.R4123.shift(2)
        )
        self.assertEqual(
            vdp.Geometry.R2341,
            vdp.Geometry.R4123.shift(-2)
        )
        self.assertEqual(
            vdp.Geometry.RHorizontal,
            vdp.Geometry.RVertical.shift()
        )

    def test_reverse_polarity(self):
        vdp = physicslab.experiment.van_der_pauw
        self.assertEqual(
            vdp.Geometry.R1432,
            vdp.Geometry.R4123.reverse_polarity()
        )
        self.assertEqual(
            vdp.Geometry.RHorizontal,
            vdp.Geometry.RHorizontal.reverse_polarity()
        )

    def test_classify_series(self):
        vdp = physicslab.experiment.van_der_pauw

        geometry_series = pd.Series([vdp.Geometry.R1234,
                                     vdp.Geometry.R3214])
        classified = vdp.Geometry.classify(geometry_series)
        target_series = pd.Series([vdp.Geometry.RVertical,
                                   vdp.Geometry.RHorizontal])

        for c, t in zip(classified, target_series):
            self.assertEqual(c, t)


if __name__ == '__main__':
    unittest.main(exit=False)  # verbosity=2)
