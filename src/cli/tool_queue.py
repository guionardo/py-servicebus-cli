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
        


def create_queue(sb_mgmt_client: ServiceBusAdministrationClient):
    pass
