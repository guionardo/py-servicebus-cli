import datetime
import json
import logging
import os
import pathlib

from src.config._cipher import _Cipher
from src.config.profiles import ProfilesConfig
from src.config.version import VersionConfig
from src.tools.logging import get_console


class ConfigStore:

    def __init__(self, file_name: str = None):
        self.log = logging.getLogger(__name__)
        self.filename = file_name or os.path.join(
            pathlib.Path().home(), '.sbcli.conf')
        self.cipher = _Cipher()
        self.key: str = self.cipher.encoded_key
        self.profiles: ProfilesConfig = ProfilesConfig({}, self.cipher)
        self.version: VersionConfig = VersionConfig({})
        self.load()

    def load(self) -> bool:
        if not os.path.isfile(self.filename):
            self.log.info('Configuration file not found: %s', self.filename)
            return False
        reset_file = False
        try:
            with open(self.filename) as f:
                data = json.loads(f.read())

            self.key = data.get('key', '')
            if not self.key:
                raise ValueError('Missing key')
            self.cipher = _Cipher(self.key)
            self.profiles = ProfilesConfig(
                data.get('profiles', {}), self.cipher)
            self.version = VersionConfig(data.get('version', {}))
            self.version.check_pypi_version()

            self.log.info('Configuration file loaded: %s', self.filename)
            return True
        except Exception as exc:
            self.log.error(
                'Failed to read configuration file %s %s', self.filename, exc)
            reset_file = True

        if reset_file:
            try:
                new_file = '{0}.{1}.error'.format(
                    self.filename,
                    datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                )
                os.rename(self.filename, new_file)
                self.log.warning(
                    'Corrupted configuration file was renamed to %s', new_file)
                get_console().warning(
                    'Corrupted configuration file was renamed to %s', new_file)
            except Exception as exc:
                self.log.error(
                    'Failed to deal with corrupted configuraton file %s: %s',
                    self.filename,
                    exc)
                get_console().warning(
                    'THERE ARE A PROBLEM WIH CONFIGURATION FILE %s',
                    self.filename)
                get_console().warning('PLEASE REMOVE IT MANNUALLY')

    def save(self) -> bool:
        data = {
            'key': self.cipher.encoded_key,
            'profiles': self.profiles.to_dict(),
            'version': self.version.to_dict()
        }
        if not self.backup_conf():
            return False
        try:
            with open(self.filename, 'w') as f:
                json.dump(data, f, ensure_ascii=True, indent=4)
            if not os.path.isfile(self.filename):
                raise FileNotFoundError(self.filename)

            self.delete_backup_conf()
            return True
        except Exception as exc:
            self.log.error('Failed to save configuration file %s: %s',
                           self.filename,
                           exc)
        self.restore_conf()

    def backup_conf(self) -> bool:
        if not os.path.isfile(self.filename):
            return True
        try:
            backup_file = self.filename+'.bkp'
            os.rename(self.filename, backup_file)
            return os.path.isfile(backup_file)
        except Exception as exc:
            self.log.error('Failed to create backup file: %s', exc)

    def delete_backup_conf(self):
        backup_file = self.filename+'.bkp'
        if os.path.isfile(backup_file):
            try:
                os.unlink(backup_file)
            except Exception as exc:
                self.log.error('Failed to delete backup file: %s', exc)
        return not os.path.isfile(backup_file)

    def restore_backup_conf(self):
        backup_file = self.filename+'.bkp'
        if not os.path.isfile(backup_file):
            self.log.error('There are no backup file: %s', backup_file)
            return
        if os.path.isfile(self.filename):
            try:
                os.unlink(self.filename)
            except Exception as exc:
                self.log.error(
                    'Cannot restore configuration backup file - %s', exc)
                return
        try:
            os.rename(backup_file, self.filename)
            self.log.info('Backup file was restored to %s', self.filename)
        except Exception as exc:
            self.log.error(
                'Cannot restore configuration backup file - %s', exc)
