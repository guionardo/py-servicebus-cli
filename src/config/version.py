from datetime import datetime, timedelta

from src import __version__
from src.tools.pypi import PyPiVersion
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

    def to_dict(self) -> dict:
        return dict(
            last_download=int(self.last_download.timestamp()),
            current_version=str(self.current_version),
            pypi_version=str(self.pypi_version))

    def check_pypi_version(self):
        if (datetime.now()-self.last_download) < timedelta(days=7):
            return
        pypi_version = PyPiVersion()
        if pypi_version.fetch():
            self.pypi_version = pypi_version.pipy_version
            self.last_download = datetime.now()

    def __repr__(self) -> str:
        return f"{self.current_version} ({self.pypi_version})"
