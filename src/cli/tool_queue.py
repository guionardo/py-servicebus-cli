import logging
import fnmatch

from azure.servicebus.management import ServiceBusAdministrationClient
from src.tools.output import Output

LOG = logging.getLogger(__name__)


def tool_queue(args):
    LOG.info('TOOL_QUEUE %s', args)

    with ServiceBusAdministrationClient \
            .from_connection_string(args.connection, logging_enable=args.debug) as sb_mgmt_client:

        if args.create:
            create_queue(sb_mgmt_client)
        elif args.list:
            list_queues(sb_mgmt_client, args)


def list_queues(sb_mgmt_client: ServiceBusAdministrationClient, args):
    details = getattr(args, 'list', Output.TEXT)
    if details == Output.TEXT:
        output = Output('queue_name')
    else:
        output = Output('queue_name',
                        'active_message_count',
                        'total_message_count',
                        'dead_letter_message_count',
                        'size_in_bytes')

    LOG.info('Getting queues properties')
    for queue_properties in sb_mgmt_client.list_queues():
        if args.filter and not fnmatch.fnmatch(queue_properties.name, args.filter):
            continue
        if details:
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

    print(output.export(details))


def create_queue(sb_mgmt_client: ServiceBusAdministrationClient):
    pass
