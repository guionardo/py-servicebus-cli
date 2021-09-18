import unittest

from src.config._cipher import _Cipher


class TestCipher(unittest.TestCase):

    def test_cipher(self):
        key = _Cipher.generate_key()

        cipher = _Cipher(key)

        secret_data = 'SECRET DATA'
        encrypted = cipher.encrypt(secret_data)
        decrypted = cipher.decrypt(encrypted)

        self.assertEqual(secret_data, decrypted)
