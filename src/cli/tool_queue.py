

from azure.servicebus.management import ServiceBusAdministrationClient


def tool_queue(args):

    with ServiceBusAdministrationClient \
            .from_connection_string(args.connection, logging_enable=args.debug) as sb_mgmt_client:

        if args.create:
            create_queue(sb_mgmt_client)
        elif args.clear_deadletter:
            clear_deadletter()


def create_queue(sb_mgmt_client: ServiceBusAdministrationClient):
    # TODO: Implementar criação de fila
    raise NotImplementedError("create_queue")


def clear_deadletter():
    # TODO: Implementar limpeza de DLQ
    raise NotImplementedError('clear_deadletter')
