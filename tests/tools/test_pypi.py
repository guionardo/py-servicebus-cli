import unittest
from src.tools.pypi import PyPiInfoFile


class TestPyPi(unittest.TestCase):

    def test_pypi(self):
        pypi = PyPiInfoFile()
        msg = pypi.update_message()
        self.assertIsNotNone(msg)
