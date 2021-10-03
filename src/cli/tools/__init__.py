import argparse
import logging
import os
import sys
from typing import Union

from src.config.store import ConfigStore

SB_CONNECTION_STRING = 'SB_CONNECTION_STRING'
QUEUE_NAME = 'Queue name'
TOPIC_NAME = 'Topic name'


def parse_conection_profile(args: argparse.Namespace,
                            config: ConfigStore) -> Union[str, Exception]:
    """
    Parses argument to get connection string from profile or connection string

    @returns connection string and error
    """
    log = logging.getLogger(__name__)
    if args.profile:
        connection = config.profiles[args.profile]
        if not connection:
            log.warning('Profile %s not found', args.profile)
            return None, Exception('Profile not found', args.profile)

        log.info('Connection from profile "%s"', args.profile)
        return connection, None
    if args.connection:
        log.info('Connection from arg %s', args.connection)
        return args.connection, None

    connection = os.getenv(SB_CONNECTION_STRING)
    if connection:
        log.info('Connection from env %s', SB_CONNECTION_STRING)
        return connection, None

    if config.profiles.default:
        connection = config.profiles[config.profiles.default]
        if not connection:
            log.warning('Default profile %s not found',
                        config.profiles.default)
            return None, Exception('Default profile not found',
                                   config.profiles.default)
        log.info('Connection from default profile %s', config.profiles.default)
        return connection, None

    return None, Exception('No connection string detected (argument, '
                           'profile or default profile)')


def setup_connection_profile_args(parser):
    connection_string = os.getenv(SB_CONNECTION_STRING)

    need_connection = ('profile' not in sys.argv) and not bool(
        connection_string)
    cs = parser.add_mutually_exclusive_group(required=need_connection)
    cs.add_argument('--connection',
                    action='store', default=connection_string,
                    help="Service bus connection string " +
                    f"(env {SB_CONNECTION_STRING})")
    cs.add_argument('--profile',
                    action='store', help='Connection profile')
