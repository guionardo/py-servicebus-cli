import logging


class Version:

    __slots__ = ['major', 'minor', 'feature', 'log']

    def __init__(self, version: str = '0.0.0'):
        self.log = logging.getLogger(__name__)
        self.major = 0
        self.minor = 0
        self.feature = 0
        version = ''.join(
            [c for c in str(version) if '0' <= c <= '9' or c == '.'])
        n = version.split('.')
        n.extend(['0', '0', '0'])

        try:
            self.major = int(n[0])
            self.minor = int(n[1])
            self.feature = int(n[2])
        except Exception as exc:
            self.log.error('Error parsing version %s : %s', version, exc)

    def __gt__(self, other: object) -> bool:
        if self.major > other.major:
            return True
        if self.minor > other.minor:
            return True
        if self.feature > other.feature:
            return True
        return False

    def __repr__(self) -> str:
        return f"Version({self.major}.{self.minor}.{self.feature})"

    def __str__(self) -> str:
        return f"v{self.major}.{self.minor}.{self.feature}"

    def is_empty(self) -> bool:
        return self.major == 0 and self.minor == 0 and self.feature == 0
