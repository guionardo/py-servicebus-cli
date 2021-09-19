import os
import unittest

from src import __version__
from src.config.store import ConfigStore


class TestConfigStore(unittest.TestCase):

    CONFIG_FILE_NAME = 'test_store.json'

    @classmethod
    def setUpClass(cls) -> None:
        if os.path.isfile(cls.CONFIG_FILE_NAME):
            os.unlink(cls.CONFIG_FILE_NAME)

        return super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        if os.path.isfile(cls.CONFIG_FILE_NAME):
            os.unlink(cls.CONFIG_FILE_NAME)

        return super().tearDownClass()

    def test_store(self):
        store = ConfigStore(self.CONFIG_FILE_NAME)
        self.assertEqual('v'+__version__, str(store.version.current_version))
        store.profiles['default'] = 'connection_string_1'
        store.profiles['prod'] = 'connection_string_2'
        self.assertFalse(store.profiles.set_default('none'))
        self.assertTrue(store.profiles.set_default('prod'))
        self.assertTrue(store.save())

        store2 = ConfigStore(self.CONFIG_FILE_NAME)
        self.assertEqual(store.profiles.default, store2.profiles.default)
        self.assertTrue(store2.save())
