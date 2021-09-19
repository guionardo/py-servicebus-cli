from datetime import datetime, timedelta

from src import __version__
from src.tools.pypi import PyPiVersion, pipy_update_message
from src.tools.version import Version


class VersionConfig:

    def __init__(self, data: dict) -> None:
        last_download = data.get('last_download', 0)
        if not isinstance(last_download, int):
            last_download = 0

        self.last_download: datetime = datetime.fromtimestamp(
            last_download)
        self.current_version: Version = Version(__version__)
        self.pypi_version: Version = Version(data.get('pypi_version', '0.0.0'))
        self.update_message = 'not checked yet'

    def to_dict(self) -> dict:
        return dict(
            last_download=int(self.last_download.timestamp()),
            current_version=str(self.current_version),
            pypi_version=str(self.pypi_version))

    def check_pypi_version(self):
        if (datetime.now()-self.last_download) < timedelta(days=7):
            self.update_message = pipy_update_message(self.pypi_version)
            return
        pypi_version = PyPiVersion()
        if pypi_version.fetch():
            self.pypi_version = pypi_version.pipy_version
            self.last_download = datetime.now()
            self.update_message = pipy_update_message(pypi_version.pipy_version)

    def __repr__(self) -> str:
        return f"{self.current_version} ({self.pypi_version})"
