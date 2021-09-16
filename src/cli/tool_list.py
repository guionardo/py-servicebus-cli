import fnmatch
import logging

from azure.servicebus.management import ServiceBusAdministrationClient
from src.tools.misc import remove_quotes
from src.tools.output import Output


LOG = logging.getLogger(__name__)


def tool_list(args):
    LOG.info('TOOL_LIST %s', args)
    with ServiceBusAdministrationClient \
            .from_connection_string(
                args.connection,
                logging_enable=args.debug) as sb_mgmt_client:
        args.queue = remove_quotes(args.queue)
        args.topic = remove_quotes(args.topic)
        if args.queue:
            _tool_list_queue(sb_mgmt_client, args)
        elif args.topic:
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
