import argparse
import os
from sys import argv

from src import __description__, __tool_name__, __version__
from src.cli.tool_topic import tool_topic
from src.cli.tools import SB_CONNECTION_STRING
from src.cli.tools.download import setup_download_tools
from src.cli.tools.list import setup_list_tools
from src.cli.tools.profiles import setup_profile_tools
from src.cli.tools.queue import setup_queue_tools
from src.cli.tools.upload import setup_upload_tools
from src.config.store import ConfigStore
from src.tools.logging import get_log_file


def setup_cli() -> argparse.ArgumentParser:
    log_file = get_log_file()
    config = ConfigStore()
    config.version.check_pypi_version()

    epilog = [
        config.version.update_message,
        'Log file: {0}'.format('disabled' if not log_file else log_file),
    ]
    parser = argparse.ArgumentParser(prog=__tool_name__,
                                     description=__description__,
                                     epilog='. '.join(epilog))
    connection_string = os.getenv(SB_CONNECTION_STRING)

    parser.add_argument('--version', action='version',
                        version=f'%(prog)s {__version__}')

    need_connection = ('profile' not in argv) and not bool(connection_string)

    cs = parser.add_mutually_exclusive_group(required=need_connection)
    cs.add_argument('--connection', required=need_connection,
                    action='store', default=connection_string,
                    help="Service bus connection string " +
                    f"(env {SB_CONNECTION_STRING})")
    cs.add_argument('--profile', required=need_connection,
                    action='store', help='Connection profile')

    parser.add_argument('--no-logging', required=False,
                        action='store_true', default=False)
    parser.add_argument('--debug', action='store_true',
                        default=False, help='Set debug level to log')

    sub_commands = parser.add_subparsers(title='actions',)

    setup_list_tools(sub_commands)

    setup_queue_tools(sub_commands)
    setup_topic_tools(sub_commands)
    setup_download_tools(sub_commands)
    setup_upload_tools(sub_commands)
    setup_profile_tools(sub_commands)

    return parser


def setup_topic_tools(sub_commands):
    p: argparse.ArgumentParser = sub_commands.add_parser('topic')
    p.set_defaults(func=tool_topic)
    p.add_argument('--create', action='store_true')
