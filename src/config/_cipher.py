import logging
from base64 import b85decode, b85encode

from cryptography.fernet import Fernet


class _Cipher:
    LOG = logging.getLogger(__name__)

    def __init__(self, key: str = None) -> None:
        if not key:
            key = self.generate_key()
        b_keys = b85decode(key)
        self._encoded_key = None
        try:
            self.cipher_suite = Fernet(b_keys)
            self._encoded_key = key
        except ValueError as exc:
            self.LOG.error('Invalid key: %s', exc)
            raise

    @property
    def encoded_key(self) -> str:
        return self._encoded_key

    def encrypt(self, data: str) -> str:
        encoded = self.cipher_suite.encrypt(data.encode('utf-8'))
        return b85encode(encoded).decode('ascii')

    def decrypt(self, encrypted: str) -> str:
        decoded = b85decode(encrypted)
        decoded = self.cipher_suite.decrypt(decoded).decode('utf-8')
        return decoded

    @classmethod
    def generate_key(cls) -> str:
        key = Fernet.generate_key()
        encoded_key = b85encode(key).decode('ascii')
        return encoded_key
