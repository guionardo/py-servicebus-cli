from azure.servicebus.management import ServiceBusAdministrationClient


def tool_topic(args):

    with ServiceBusAdministrationClient \
            .from_connection_string(args.connection, logging_enable=args.debug) as sb_mgmt_client:

        if args.create:
            create_topic(sb_mgmt_client)


def create_topic(sb_mgmt_client: ServiceBusAdministrationClient):
    # TODO: Implementar tool topic
    raise NotImplementedError('create_topic')
