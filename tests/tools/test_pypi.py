import unittest

from src import __version__
from src.tools.pypi import PyPiVersion, pipy_update_message


class TestPyPi(unittest.TestCase):

    def test_pypi_update_message(self):
        msg = pipy_update_message(pipy_version='0.0.1')
        self.assertTrue('version ahead' in msg)

        msg = pipy_update_message(pipy_version=__version__)
        self.assertTrue('latest version' in msg)

        msg = pipy_update_message(pipy_version='99.99.99')
        self.assertTrue('new version' in msg)

    def test_pypi_version_request(self):
        pipy = PyPiVersion()
        status, _ = pipy._request('https://google.com')
        self.assertIsNot(-1, status)

    def test_pypi_version_get_pypi_data(self):
        pypi = PyPiVersion()
        data = pypi.get_pypi_data()
        self.assertGreater(len(data), 0)

    def test_pypi_fetch(self):
        pypi = PyPiVersion()
        self.assertTrue(pypi.fetch())
