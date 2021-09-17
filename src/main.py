from src.cli.setup import setup_cli
from src.tools.logging import get_console, setup_logging


def main():
    parser = setup_cli()
    try:
        args = parser.parse_args()
        setup_logging(args.no_logging, args.debug)
        get_console().debug('Args: %s', args)

        if hasattr(args, 'func'):
            args.func(args)
    except NotImplementedError as exc:
        get_console().error('Not implemented: %s', exc)
    except Exception as exc:
        get_console().error('Error: %s', exc)
