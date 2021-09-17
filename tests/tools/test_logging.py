import logging
import unittest

from src.tools.logging import (get_console, get_log_file, get_logger,
                               reset_logging, setup_done, setup_logging)


class TestLogging(unittest.TestCase):

    def setUp(self) -> None:
        reset_logging()
        return super().setUp()

    def test_setup_logging_no_logging(self):
        setup_logging(no_logging=True, debug=False)
        self.assertTrue(setup_done())

    def test_setup_logging_no_debug(self):
        setup_logging(no_logging=False, debug=False)
        self.assertTrue(setup_done())

