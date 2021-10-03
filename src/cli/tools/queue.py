import argparse

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.servicebus import ServiceBusClient
from azure.servicebus._common.constants import (ServiceBusReceiveMode,
                                                ServiceBusSubQueue)
from azure.servicebus.management import ServiceBusAdministrationClient
from src.cli.tools import (parse_conection_profile,
                           setup_connection_profile_args)
from src.config.store import ConfigStore
from src.tools.sb import validate_queue_name
from tqdm import tqdm


def setup_queue_tools(sub_commands):
    p: argparse.ArgumentParser = sub_commands.add_parser(
        'queue',
        help='Queue management')
    p.set_defaults(func=tool_queue)
    sc = p.add_mutually_exclusive_group(required=True)

    sc.add_argument('--create', action='store',
                    metavar='queue_name',
                    help='Create queue')
    sc.add_argument('--clear-dead-letter', action='store',
                    metavar='queue_name',
                    help='Empty dead letter queue')
    sc.add_argument('--delete', action='store',
                    metavar='queue_name', help='Delete queue')

    setup_connection_profile_args(p)


def tool_queue(args: argparse.Namespace,
               parser: argparse.ArgumentParser):
    config = ConfigStore()
    connection, err = parse_conection_profile(args, config)
    if err:
        parser.exit(1, str(err))

    with ServiceBusAdministrationClient \
            .from_connection_string(
                connection,
                logging_enable=args.debug) as sb_mgmt_client:
        if args.create:
            create_queue(sb_mgmt_client, args, parser)
        elif args.delete:
            delete_queue(sb_mgmt_client, args, parser)
        elif args.clear_dead_letter:
            clear_deadletter(sb_mgmt_client, args, parser)


def create_queue(sb_mgmt_client: ServiceBusAdministrationClient,
                 args: argparse.Namespace,
                 parser: argparse.ArgumentParser):
    if not validate_queue_name(args.create, False):
        parser.exit(1, f'Invalid queue name "{args.create}"')

    try:
        _ = sb_mgmt_client.create_queue(args.create)
        parser.exit(
            0, f'Queue "{args.create}" created with default properties')
    except ResourceExistsError:
        parser.exit(1, f'Queue "{args.create}" exists')
    except Exception as exc:
        parser.exit(1, f'Exception on creating queue: {exc}')


def clear_deadletter(sb_mgmt_client: ServiceBusAdministrationClient,
                     args: argparse.Namespace,
                     parser: argparse.ArgumentParser):
    if not validate_queue_name(args.clear_dead_letter, False):
        parser.exit(1, f'Invalid queue name "{args.clear_dead_letter}"')
    config = ConfigStore()
    connection, err = parse_conection_profile(args, config)
    if err:
        parser.exit(1, str(err))
    try:
        queue = sb_mgmt_client.get_queue_runtime_properties(
            args.clear_dead_letter)
        if queue.dead_letter_message_count == 0:
            parser.exit(
                0, f'Queue "{args.clear_dead_letter}" has no messages in dead letter')
    except ResourceNotFoundError:
        parser.exit(1, f'Queue "{args.clear_dead_letter}" not found')

    cleaned = 0
    with ServiceBusClient.from_connection_string(connection) as client:
        with tqdm(total=queue.dead_letter_message_count,
                  desc='Emptying DLQ',
                  unit='msg') as pbar:
            with client.get_queue_receiver(
                    args.clear_dead_letter,
                    sub_queue=ServiceBusSubQueue.DEAD_LETTER,
                    receive_mode=ServiceBusReceiveMode.RECEIVE_AND_DELETE) as receiver:
                for _ in receiver.receive_messages(max_message_count=queue.dead_letter_message_count):
                    pbar.update(1)
                    cleaned += 1
    parser.exit(
        0, f'Queue "{args.clear_dead_letter}" with {cleaned} messages removed from dead letter')


def delete_queue(sb_mgmt_client: ServiceBusAdministrationClient,
                 args: argparse.Namespace,
                 parser: argparse.ArgumentParser):
    if not validate_queue_name(args.delete, False):
        parser.exit(1, f'Invalid queue name "{args.delete}"')
    try:
        sb_mgmt_client.delete_queue(args.delete)
        parser.exit(0, f'Queue "{args.delete}" deleted')
    except ResourceNotFoundError:
        parser.exit(1, f'Queue "{args.delete}" not found')
    except Exception as exc:
        parser.exit(1, f'Exception on deleting queue: {exc}')
