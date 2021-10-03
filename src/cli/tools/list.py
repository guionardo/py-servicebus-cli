import argparse
import fnmatch
import logging

from azure.servicebus.management import ServiceBusAdministrationClient
from src.cli.tools import (parse_conection_profile,
                           setup_connection_profile_args)
from src.config.store import ConfigStore
from src.tools.misc import remove_quotes
from src.tools.output import Output

LOG = logging.getLogger(__name__)


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
    setup_connection_profile_args(p)


def tool_list(args: argparse.Namespace,
              parser: argparse.ArgumentParser = None):
    config = ConfigStore()
    connection, err = parse_conection_profile(args, config)
    if err:
        parser.exit(1, str(err))

    with ServiceBusAdministrationClient \
            .from_connection_string(
                connection,
                logging_enable=args.debug) as sb_mgmt_client:
        if args.queue:
            args.queue = remove_quotes(args.queue)
            _tool_list_queue(sb_mgmt_client, args)
        elif args.topic:
            args.topic = remove_quotes(args.topic)
            _tool_list_topic(sb_mgmt_client, args)


def _tool_list_queue(sb_mgmt_client: ServiceBusAdministrationClient, args):
    if args.type == Output.TEXT:
        output = Output('queue_name')
    else:
        output = Output('queue_name',
                        'active_message_count',
                        'total_message_count',
                        'dead_letter_message_count',
                        'size_in_bytes')

    LOG.info('Getting queues properties')
    for queue_properties in sb_mgmt_client.list_queues():
        if args.queue and not fnmatch.fnmatch(queue_properties.name,
                                              args.queue):
            continue
        if args.type != Output.TEXT:
            runtime_properties = sb_mgmt_client.get_queue_runtime_properties(
                queue_properties.name)
            LOG.info('+ %s: %s', queue_properties, runtime_properties)
            output.add(queue_properties.name,
                       runtime_properties.active_message_count,
                       runtime_properties.total_message_count,
                       runtime_properties.dead_letter_message_count,
                       runtime_properties.size_in_bytes
                       )
        else:
            LOG.info('+ %s', queue_properties)
            output.add(queue_properties.name)

    print(output.export(args.type))


def _tool_list_topic(sb_mgmt_client: ServiceBusAdministrationClient, args):
    output = Output('topic_name')
    LOG.info('Getting topics properties')
    for topic_properties in sb_mgmt_client.list_topics():
        if args.topic and not fnmatch.fnmatch(topic_properties.name,
                                              args.topic):
            continue
        LOG.info('+ %s', topic_properties)
        output.add(topic_properties.name)

    print(output.export(args.type))
