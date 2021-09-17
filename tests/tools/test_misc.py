import unittest

from src.tools.misc import remove_quotes


class TestMisc(unittest.TestCase):

    def test_remove_quotes(self):
        test_case = '"Quoted text"'
        self.assertEqual("Quoted text", remove_quotes(test_case))
