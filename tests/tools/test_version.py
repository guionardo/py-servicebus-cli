import unittest

from src.tools.pypi import Version


class TestVersion(unittest.TestCase):

    def test_versions(self):
        v1 = Version('0.0.3')
        v2 = Version('0.0.2')
        self.assertGreater(v1, v2)
