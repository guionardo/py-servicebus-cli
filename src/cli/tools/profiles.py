import argparse
import sys

from src.config.store import ConfigStore
from src.tools.output import Output
from src.tools.sb import ServiceBusConnectionString

FAILED_TO_SAVE = 'Failed to save configuration file'


def setup_profile_tools(sub_commands):
    p: argparse.ArgumentParser = sub_commands.add_parser(
        'profile', help='Connection profiles')
    p.set_defaults(func=tool_profile)
    sc = p.add_mutually_exclusive_group(required=True)

    sc.add_argument('--set', action='store', metavar='PROFILE',
                    help='Set profile and connection string (add --connection argument)')
    sc.add_argument('--delete', action='store', metavar='PROFILE',
                    help='Delete profile')
    sc.add_argument('--list', action='store_true', help='List profiles')
    sc.add_argument('--default', action='store', metavar='PROFILE',
                    help='Set default profile')
    required_connection = 'profile' in sys.argv and '--set' in sys.argv

    p.add_argument('--connection', required=required_connection,
                   action='store',
                   help="Connection string (used with --set)")

    p.add_argument('--output', required=False,
                   action='store', default=Output.TEXT, choices=Output.CHOICES)


def tool_profile(args: argparse.Namespace,
                 parser: argparse.ArgumentParser = None):
    config = ConfigStore()

    if args.set:
        _tool_profile_set(args, parser, config)
    elif args.delete:
        _tool_profile_delete(args, parser, config)
    elif args.list:
        _tool_profile_list(args, parser, config)
    elif args.default:
        _tool_profile_default(args, parser, config)


def _tool_profile_set(args: argparse.Namespace,
                      parser: argparse.ArgumentParser,
                      config: ConfigStore):
    try:
        ServiceBusConnectionString(args.connection)
    except Exception as exc:
        parser.exit(1, str(exc))

    config.profiles[args.set] = args.connection
    if not config.save():
        parser.exit(1, FAILED_TO_SAVE)

    parser.exit(0, f'Added profile {args.set} = {args.connection}')


def _tool_profile_delete(args: argparse.Namespace,
                         parser: argparse.ArgumentParser,
                         config: ConfigStore):
    connection = config.profiles[args.delete]
    if not connection:
        parser.exit(1, f'There are no profile "{args.delete}"')
    config.profiles[args.delete] = ''
    remove_default = ""
    if config.profiles.default == args.delete:
        config.profiles.set_default('')
        remove_default = " (there are no default profile now)"
    if not config.save():
        parser.exit(1, FAILED_TO_SAVE)
    parser.exit(0, f'Removed profile {args.delete}{remove_default}')


def _tool_profile_list(args: argparse.Namespace,
                       parser: argparse.ArgumentParser,
                       config: ConfigStore):
    output = Output('profile', 'endpoint')
    for profile in config.profiles:
        sb_cs = ServiceBusConnectionString(config.profiles[profile])
        output.add(profile, sb_cs.endpoint)

    parser.exit(0, output.export(args.output))


def _tool_profile_default(args: argparse.Namespace,
                          parser: argparse.ArgumentParser,
                          config: ConfigStore):
    connection = config.profiles[args.default]
    if not connection:
        parser.exit(1, f'There are no profile "{args.delete}"')
    config.profiles.set_default(args.default)
    if not config.save():
        parser.exit(1, FAILED_TO_SAVE)
    parser.exit(0, f'Set default profile {args.default}')
