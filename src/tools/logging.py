import logging
import os
import pathlib
from logging.handlers import TimedRotatingFileHandler

from src import __tool_name__

_SETUP_DONE = False
_LOGGER = None
_FORMAT = '%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s'


def setup_logging(no_logging: bool, debug: bool):
    global _SETUP_DONE
    if _SETUP_DONE:
        return
    if no_logging:
        _SETUP_DONE = True
        return

    log_file = get_log_file()

    level = logging.DEBUG if debug else logging.INFO

    handlers = []
    if debug:
        handlers.append(logging.StreamHandler())
    if log_file:
        handlers.append(TimedRotatingFileHandler(log_file, when="midnight",
                                                 interval=1, backupCount=7))

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(message)s'))

    if handlers:
        logging.basicConfig(format=_FORMAT,
                            handlers=handlers, level=level)

        logging.getLogger(__name__).info('INIT')
        logging.getLogger('console').addHandler(console_handler)
    else:
        logging.basicConfig(format='%(message)s', handlers=[
                            console_handler], level=logging.INFO)

    _SETUP_DONE = True


def get_log_file() -> str:
    log_dir = os.path.join(str(pathlib.Path.home()), '.log')
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception:
        return ''
    return os.path.join(log_dir, __tool_name__+'.log')


def get_logger() -> logging.Logger:
    return _LOGGER
