import argparse
import os
import unittest


from src.cli.tools import parse_conection_profile, SB_CONNECTION_STRING
from src.config.store import ConfigStore

CONNECTION = 'connection'


class TestParseConnection(unittest.TestCase):

    def test_arg_profile_found(self):
        config = ConfigStore('.tmp')
        config.profiles['default'] = CONNECTION

        args = argparse.Namespace(profile='default')
        connection, _ = parse_conection_profile(args, config)

        self.assertEqual(CONNECTION, connection)

    def test_arg_profile_not_found(self):
        config = ConfigStore('.tmp')
        args = argparse.Namespace(profile='default')
        _, err = parse_conection_profile(args, config)

        self.assertIsNotNone(err)

    def test_arg_connection(self):
        config = ConfigStore('.tmp')
        args = argparse.Namespace(connection=CONNECTION, profile=None)
        connection, _ = parse_conection_profile(args, config)
        self.assertEqual(CONNECTION, connection)

    def test_env_connection(self):
        config = ConfigStore('.tmp')
        args = argparse.Namespace(connection=None, profile=None)
        os.environ.update({SB_CONNECTION_STRING: CONNECTION})
        connection, _ = parse_conection_profile(args, config)
        self.assertEqual(CONNECTION, connection)
        del(os.environ[SB_CONNECTION_STRING])

    def test_profile_default(self):
        config = ConfigStore('.tmp')
        config.profiles['default'] = CONNECTION
        config.profiles.set_default('default')
        args = argparse.Namespace(connection=None, profile=None)
        connection, _ = parse_conection_profile(args, config)
        self.assertEqual(CONNECTION, connection)

    def test_profile_default_not_found(self):
        config = ConfigStore('.tmp')
        config.profiles['default'] = CONNECTION
        config.profiles.default = 'default_not_existent'
        args = argparse.Namespace(connection=None, profile=None)
        _, err = parse_conection_profile(args, config)
        self.assertIsNotNone(err)

    def test_connection_unknown(self):
        config = ConfigStore('.tmp')
        os.environ.update({SB_CONNECTION_STRING: ""})
        args = argparse.Namespace(connection=None, profile=None)
        _, err = parse_conection_profile(args, config)
        self.assertIsNotNone(err)
