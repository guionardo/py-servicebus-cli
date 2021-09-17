import os
import shutil
import unittest

from src.tools.files import get_files


class TestFiles(unittest.TestCase):

    TMP_FOLDER = '.tmp_test'

    @classmethod
    def setUpClass(cls) -> None:

        os.makedirs(cls.TMP_FOLDER, exist_ok=True)
        for n in range(10):
            with open(os.path.join(cls.TMP_FOLDER, str(n)+'.tmp'), 'w') as f:
                f.write('')
        for n in range(5):
            os.makedirs(os.path.join(cls.TMP_FOLDER, f'f{n}'))
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.TMP_FOLDER, ignore_errors=True)
        return super().tearDownClass()

    def test_get_files(self):
        files = get_files(self.TMP_FOLDER, 5)
        self.assertEqual(5, len(files))
