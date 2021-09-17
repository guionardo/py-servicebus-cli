import datetime
import json
import logging
import os
import ssl
import urllib.request

from src import __package_name__, __version__, __description__
from src.tools.version import Version


class PyPiInfoFile:

    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.last_download = 0
        self.current_version = Version(__version__)
        self.pipy_version = Version()
        self.pipy_downloads = {"last_day": -1,
                               "last_month": -1,
                               "last_week": -1}
        self.open_file()
        self.verify()

    @classmethod
    def file_name(cls) -> str:
        return os.path.join(
            os.path.expanduser('~'), f'.{__package_name__}')

    def update_message(self) -> str:
        if self.pipy_version.is_empty():
            return 'There is no data from pypi'

        if self.pipy_version > self.current_version:
            return 'There are a new version of {0}: {1} - run "pip install {2} --upgrade"'.format(
                __description__,
                self.pipy_version,
                __package_name__
            )
        if self.current_version > self.pipy_version:
            return 'You are using a version ahead ({0}) of pypi ({1})'.format(
                self.current_version,
                self.pipy_version
            )
        return 'You are using the latest version {0}'.format(self.current_version)

    def open_file(self):
        file = self.file_name()
        if os.path.isfile(file):
            try:
                with open(file) as f:
                    data = json.loads(f.read())
                self.last_download = data.get('last_download', 0)
                self.parse_data(data.get('project', {}))
                return
            except Exception as exc:
                self.log.warning('Failed to read/parse info file %s: %s',
                                 self.file, exc)
                os.unlink(file)
        self.last_download = 0

    @property
    def download_time(self) -> datetime.datetime:
        if self.last_download:
            return datetime.datetime.fromtimestamp(self.last_download)
        return datetime.datetime(datetime.MINYEAR, 1, 1)

    @download_time.setter
    def download_time(self, time: datetime.datetime):
        self.last_download = int(time.timestamp())

    def update(self) -> bool:
        """ Download data and update fields"""
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
        self.download_time = datetime.datetime.now()
        file_data = {
            'last_download': self.last_download,
            'project': data
        }
        with open(self.file_name(), 'w') as f:
            f.write(json.dumps(file_data, indent=2))

    def parse_data(self, project: dict):
        info = project.get('info', {})
        if not info:
            raise ValueError('missing "info" field')
        version = info.get('version', '')
        if not version:
            raise ValueError('missing "version" field')
        self.pipy_version = Version(version)

    def verify(self):
        t = datetime.datetime.now()-self.download_time
        if t < datetime.timedelta(days=7):
            self.log.info(
                'Last download @ %s - dont need to verify', self.download_time)
            return
        if not self.update():
            return

    def get_pypi_data(self) -> dict:
        url = f'https://pypi.org/pypi/{__package_name__}/json'
        try:
            gcontext = ssl.SSLContext()
            req = urllib.request.Request(
                url, headers={'Accept': 'application/json'})

            conn = urllib.request.urlopen(req, context=gcontext)
            if 199 < conn.status < 400:
                return json.loads(conn.read())
            self.log.warning('PyPi package request failed: %s %s',
                             conn.status, conn.msg)

        except Exception as exc:
            self.log.error('PyPi package request exception: %s', exc)

        return {}
