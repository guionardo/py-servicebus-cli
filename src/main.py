import logging

from src.cli.setup import setup_cli
from src.tools.logging import setup_logging


def main():
    parser = setup_cli()
    try:
        args = parser.parse_args()
        setup_logging(args.no_logging, args.debug)
        logging.getLogger('console').debug('Args: %s', args)

        if hasattr(args, 'func'):
            args.func(args)
    except Exception as exc:
        logging.getLogger('console').error('Error: %s', exc)
