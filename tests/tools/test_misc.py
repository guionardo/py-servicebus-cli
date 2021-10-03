import unittest

from src.tools.misc import get_bulks, remove_quotes


class TestMisc(unittest.TestCase):

    def test_remove_quotes(self):
        test_case = '"Quoted text"'
        self.assertEqual("Quoted text", remove_quotes(test_case))

    def test_get_bulks(self):
        data = [str(n) for n in range(35)]
        bulks = get_bulks(data, 10)
        self.assertEqual(4, len(bulks))
