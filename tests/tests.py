# -*- coding: utf-8 -*-
"""
Testing of :mod:`physicslab`.

.. note::
    Run this script directly to run a :mod:`unittest`.
"""


import os
import re
import unittest

import pycodestyle

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


# class TestBlueprintMethods(unittest.TestCase):

#     @classmethod
#     def setUpClass(cls):
#         pass
#         cls.blueprint =

#     def test_parse_int(self):
#         self.assertEqual(0, 0)


if __name__ == '__main__':
    unittest.main(exit=False)  # verbosity=2
