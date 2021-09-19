import argparse
import logging
import os
from typing import Union

from src.config.store import ConfigStore

SB_CONNECTION_STRING = 'SB_CONNECTION_STRING'


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
