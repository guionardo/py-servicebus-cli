import unittest

from src import __version__
from src.config.version import VersionConfig


class TestVersionConfig(unittest.TestCase):

    def test_version(self):
        v = VersionConfig({})
        self.assertDictEqual({
            'last_download': 0,
            'current_version': 'v'+__version__,
            'pypi_version': 'v0.0.0'
        }, v.to_dict())
