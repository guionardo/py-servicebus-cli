import json
import logging
import ssl
import urllib.request
from typing import Union

from src import __description__, __package_name__, __version__
from src.tools.version import Version


class PyPiVersion:

    def __init__(self):
        self.pipy_version = Version()
        self.log = logging.getLogger(__name__)

    def fetch(self) -> bool:
        data = self.get_pypi_data()
        info = data.get('info', {})
        if not info:
            self.log.warning('Request data failed - missing "info" field')
            return False
        downloads = info.get('downloads', {})
        if not downloads:
            self.log.warning(
                'Request data failed - missing "info.downloads" field')
            return False
        version = info.get('version', '')
        if not version:
            self.log.warning(
                'Request data failed - missing "info.version" field')
            return False
        self.pipy_version = Version(version)
        return True

    def get_pypi_data(self) -> dict:
        url = f'https://pypi.org/pypi/{__package_name__}/json'
        status, body = self._request(url)
        if 199 < status < 400:
            try:
                return json.loads(body)
            except Exception as exc:
                self.log.error('PyPi API response is invalid: %s', exc)
        else:
            self.log.error('PyPi package request failed: %s', status)

        return {}

    def _request(self, url: str) -> Union[int, bytes]:
        """ HTTP Request """
        try:
            gcontext = ssl.SSLContext()
            req = urllib.request.Request(
                url, headers={'Accept': 'application/json'})

            with urllib.request.urlopen(req, context=gcontext) as conn:
                self.log.info('Request: %s -> %s %s',
                              url, conn.status, conn.reason)
                return (conn.status, conn.read())
        except Exception as exc:
            self.log.error('HTTP request failed: %s', exc)
        return (-1, None)

    def update_message(self) -> str:
        return pipy_update_message(self.pipy_version)


def pipy_update_message(pipy_version) -> str:
    if isinstance(pipy_version, str):
        pipy_version = Version(pipy_version)
    if not isinstance(pipy_version, Version):
        raise ValueError('Invalid pipy_version', pipy_version)
    current_version = Version(__version__)
    if pipy_version > current_version:
        return 'There are a new version of {0}: {1} -'\
            ' run "pip install {2} --upgrade"'.format(
                __description__,
                pipy_version,
                __package_name__
            )
    if current_version > pipy_version:
        return 'You are using a version ahead ({0}) of pypi ({1})'.format(
            current_version,
            pipy_version
        )
    return f'You are using the latest version {current_version}'
