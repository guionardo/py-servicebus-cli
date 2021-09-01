import argparse
import os

from src import __description__, __tool_name__, __version__
from src.cli.tool_queue import tool_queue
from src.cli.tool_topic import tool_topic
from src.tools.logging import get_log_file
from src.tools.output import Output

SB_CONNECTION_STRING = 'SB_CONNECTION_STRING'


def setup_cli() -> argparse.ArgumentParser:
    log_file = get_log_file()
    epilog = [
        'Log file: {0}'.format('disabled' if not log_file else log_file)
    ]
    parser = argparse.ArgumentParser(prog=__tool_name__,
                                     description=__description__,
                                     epilog='\n'.join(epilog))
    connection_string = os.getenv(SB_CONNECTION_STRING)

    parser.add_argument('--version', action='version',
                        version=f'%(prog)s {__version__}')
    parser.add_argument('--connection', required=not bool(
        connection_string), action='store', default=connection_string,
        help=f"Service bus connection string (env {SB_CONNECTION_STRING})")
    parser.add_argument('--no-logging', required=False,
                        action='store_true', default=False)
    parser.add_argument('--debug', action='store_true',
                        default=False, help='Set debug level to log')

    sub_commands = parser.add_subparsers()
    setup_queue_tools(sub_commands)
    setup_topic_tools(sub_commands)
    return parser


def setup_queue_tools(sub_commands):
    p: argparse.ArgumentParser = sub_commands.add_parser('queue')
    p.set_defaults(func=tool_queue)
    sc = p.add_mutually_exclusive_group(required=True)

    sc.add_argument('--list', action='store',
                    default=Output.TEXT, choices=Output.CHOICES)
    sc.add_argument('--create', action='store')

    p.add_argument('--filter', action='store', default=None, required=False,
                   help='Filter for select queue name. You can use * and ?')


def setup_topic_tools(sub_commands):
    p: argparse.ArgumentParser = sub_commands.add_parser('topic')
    p.set_defaults(func=tool_topic)
    sc = p.add_mutually_exclusive_group(required=True)
    sc.add_argument('--list', action='store_true')
    sc.add_argument('--create', action='store_true')
