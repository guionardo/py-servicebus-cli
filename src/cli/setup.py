import argparse
import os
from sys import argv

from src import __description__, __tool_name__, __version__
from src.cli.tool_queue import tool_queue
from src.cli.tool_topic import tool_topic
from src.cli.tool_upload import tool_upload
from src.cli.tools import QUEUE_NAME, SB_CONNECTION_STRING, TOPIC_NAME
from src.cli.tools.download import setup_download_tools
from src.cli.tools.list import setup_list_tools
from src.cli.tools.profiles import setup_profile_tools
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

    # if need_connection:

    cs = parser.add_mutually_exclusive_group(required=need_connection)
    cs.add_argument('--connection', required=need_connection,
                    action='store', default=connection_string,
                    help="Service bus connection string " +
                    f"(env {SB_CONNECTION_STRING})")
    cs.add_argument('--profile', required=need_connection,
                    action='store', help='Connection profile')

    # parser.add_argument('--connection', required=need_connection,
    #                     action='store', default=connection_string,
    #                     help=f"Service bus connection string (env {SB_CONNECTION_STRING})")
    parser.add_argument('--no-logging', required=False,
                        action='store_true', default=False)
    parser.add_argument('--debug', action='store_true',
                        default=False, help='Set debug level to log')

    sub_commands = parser.add_subparsers()

    setup_list_tools(sub_commands)

    setup_queue_tools(sub_commands)
    setup_topic_tools(sub_commands)
    setup_download_tools(sub_commands)
    setup_upload_tools(sub_commands)
    setup_profile_tools(sub_commands)

    return parser


def setup_upload_tools(sub_comands):
    p: argparse.ArgumentParser = sub_comands.add_parser(
        'upload', help='Upload message')
    p.set_defaults(func=tool_upload)
    p.add_argument('--source', action='store',
                   help='Source files (you can use mask)', required=True)
    p.add_argument('--max-count', action='store', type=int,
                   default=0, help='Maximum message count')
    sc = p.add_mutually_exclusive_group(required=True)
    sc.add_argument('--queue', action='store', help=QUEUE_NAME)
    sc.add_argument('--topic', action='store', help=TOPIC_NAME)


def setup_queue_tools(sub_commands):
    p: argparse.ArgumentParser = sub_commands.add_parser(
        'queue',
        help='Queue management')
    p.set_defaults(func=tool_queue)
    sc = p.add_mutually_exclusive_group(required=True)

    sc.add_argument('--create', action='store',
                    metavar='queue_name', help='Create queue')
    sc.add_argument('--clear-dead-letter', action='store',
                    metavar='queue_name',
                    help='Empty dead letter queue')


def setup_topic_tools(sub_commands):
    p: argparse.ArgumentParser = sub_commands.add_parser('topic')
    p.set_defaults(func=tool_topic)
    p.add_argument('--create', action='store_true')
