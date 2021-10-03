import json
import unittest

from src.cli.tools.download import _get_extension


class TestDownload(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.JSON = json.dumps(
            dict(name="Test", value=1234, enabled=True)).encode('utf-8')
        cls.XML = '''<root><doc arg="abcd">
        <field1 name="test">value</field1>
        <field2 name="test2">value2</field2>
        </doc></root>'''.encode(
            'utf-8')
        cls.CSV = 'user,name\nguionardo,"Guionardo"\nlinux,"Linus"'.encode(
            'utf-8')
        cls.TXT = 'USERNAME=ABCD'.encode('ascii')
        cls.BIN = bytearray(range(256))
        return super().setUpClass()

    def test_get_extension_json(self):
        ext = _get_extension(self.JSON)
        self.assertEqual('.json', ext)

    def test_get_extension_xml(self):
        ext = _get_extension(self.XML)
        self.assertEqual('.xml', ext)

    def test_get_extension_csv(self):
        ext = _get_extension(self.CSV)
        self.assertEqual('.csv', ext)

    def test_get_extension_txt(self):
        ext = _get_extension(self.TXT)
        self.assertEqual('.txt', ext)

    def test_get_extension_bin(self):
        ext = _get_extension(self.BIN)
        self.assertEqual('.bin', ext)
