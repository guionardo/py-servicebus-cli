import unittest

from src.tools.output import Output


class TestOutput(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.output = Output('name', 'age', 'address')
        cls.output.add('Guionardo', 43, 'localhost')
        cls.output.add('Benjamin', 7, 'there')
        return super().setUpClass()

    def test_output_text(self):
        case = self.output.export(Output.TEXT)

        self.assertEqual(
            'Guionardo| 43|localhost\nBenjamin |  7|there    ', case)

    def test_output_csv(self):
        case = self.output.export(Output.CSV)

        self.assertEqual(
            'name,age,address\r\nGuionardo,43,localhost\r\nBenjamin,7,there\r\n', case)

    def test_output_table(self):
        case = self.output.export(Output.TABLE)
        print(case)

        self.assertEqual("""+---------+---+---------+
|name     |age|address  |
+---------+---+---------+
|Guionardo| 43|localhost|
|Benjamin |  7|there    |
+---------+---+---------+
""", case)
