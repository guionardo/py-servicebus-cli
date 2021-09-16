import argparse
import os

from src import __description__, __tool_name__, __version__
from src.cli.tool_download import tool_download
from src.cli.tool_list import tool_list
from src.cli.tool_queue import tool_queue
from src.cli.tool_topic import tool_topic
from src.cli.tool_upload import tool_upload
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

    setup_list_tools(sub_commands)
    # setup_peek_tools(sub_commands)
    setup_queue_tools(sub_commands)
    # setup_topic_tools(sub_commands)
    setup_download_tools(sub_commands)
    setup_upload_tools(sub_commands)

    return parser


def setup_list_tools(sub_commands):
    p: argparse.ArgumentParser = sub_commands.add_parser(
        'list', help='List entities')
    p.set_defaults(func=tool_list)
    sc = p.add_mutually_exclusive_group(required=True)
    sc.add_argument('--queue', action='store',
                    help="Queue name (allow mask * and ?)")
    sc.add_argument('--topic', action='store',
                    help='Topic name (allow mask * and ?)')
    p.add_argument('--type', action='store',
                   default=Output.TEXT, choices=Output.CHOICES)


def setup_peek_tools(sub_commands):
    p: argparse.ArgumentParser = sub_commands.add_parser(
        'peek', help='Peek message')
    p.set_defaults(func=tool_list)
    sc = p.add_mutually_exclusive_group(required=True)
    sc.add_argument('--queue', action='store',
                    help="Queue name")
    sc.add_argument('--topic', action='store',
                    help='Topic name')


def setup_download_tools(sub_commands):
    p: argparse.ArgumentParser = sub_commands.add_parser(
        'download', help='Download message')
    p.set_defaults(func=tool_download)
    p.add_argument('--output', '-o', action='store',
                   help='Output folder (default = queue/topic name)')
    p.add_argument('--file-prefix', action='store', help='Fileprefix')
    p.add_argument('--dead-letter', action='store_true',
                   help='Dead letter queue')
    p.add_argument('--timeout', action='store', type=int,
                   default=30, help='Timeout in seconds')
    sc = p.add_mutually_exclusive_group(required=True)
    sc.add_argument('--queue', action='store', help='Queue name')
    sc.add_argument('--topic', action='store', help='Topic name')

    sq = p.add_mutually_exclusive_group(required=False)
    sq.add_argument('--max-count', action='store', type=int,
                    default=0, help='Maximum message count')
    sq.add_argument('--all', action='store_true', help='Download all messages')


def setup_upload_tools(sub_comands):
    p: argparse.ArgumentParser = sub_comands.add_parser(
        'upload', help='Upload message')
    p.set_defaults(func=tool_upload)
    p.add_argument('--source', action='store',
                   help='Source files (you can use mask)', required=True)
    p.add_argument('--max-count', action='store', type=int,
                   default=0, help='Maximum message count')
    sc = p.add_mutually_exclusive_group(required=True)
    sc.add_argument('--queue', action='store', help='Queue name')
    sc.add_argument('--topic', action='store', help='Topic name')


def setup_queue_tools(sub_commands):
    p: argparse.ArgumentParser = sub_commands.add_parser(
        'queue',
        help='Queue management')
    p.set_defaults(func=tool_queue)
    sc = p.add_mutually_exclusive_group(required=True)

    sc.add_argument('--list', action='store',
                    default=Output.TEXT, choices=Output.CHOICES)
    sc.add_argument('--create', action='store', help='Create queue')
    sc.add_argument('--clear-dead-leter', action='store',
                    help='Empty dead letter queue')

    p.add_argument('--filter', action='store', default=None, required=False,
                   help='Filter for select queue name. You can use * and ?')


def setup_topic_tools(sub_commands):
    p: argparse.ArgumentParser = sub_commands.add_parser('topic')
    p.set_defaults(func=tool_topic)
    sc = p.add_mutually_exclusive_group(required=True)
    sc.add_argument('--list', action='store_true')
    sc.add_argument('--create', action='store_true')
