from src.cli.setup import setup_cli
from src.tools.logging import get_console, setup_logging


def main():
    parser = setup_cli()
    try:
        args = parser.parse_args()
        setup_logging(args.no_logging, args.debug)
        get_console().debug('Args: %s', args)

        if hasattr(args, 'func'):
            args.func(args, parser)
        else:
            parser.print_help()
    except NotImplementedError as exc:
        get_console().error('Not implemented: %s', exc)
        get_console().info(
            'Check or open a issue: https://github.com/guionardo/py-servicebus-cli/issues')
    except Exception as exc:
        get_console().error('Error: %s', exc)
