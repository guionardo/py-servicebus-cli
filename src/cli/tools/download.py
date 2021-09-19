import argparse
import sys
import json
import os

import xmltodict
from azure.servicebus import ServiceBusClient, ServiceBusSubQueue
from src.cli.tools import QUEUE_NAME, TOPIC_NAME, parse_conection_profile
from src.tools.logging import get_console


def setup_download_tools(sub_commands):
    p: argparse.ArgumentParser = sub_commands.add_parser(
        'download', help='Download message')
    p.set_defaults(func=tool_download)
    p.add_argument('--output', '-o', action='store',
                   help='Output folder (default = queue/topic name)')
    p.add_argument('--file-prefix', action='store', help='Fileprefix')
    p.add_argument('--dead-letter', action='store_true',
                   help='Dead letter queue')
    p.add_argument('--timeout', action='store', type=int,
                   default=30, help='Timeout in seconds')
    p.add_argument('--peek', action='store_true',
                   help='Peek (does not complete message in queue)')
    sc = p.add_mutually_exclusive_group(required=True)
    sc.add_argument('--queue', action='store', help=QUEUE_NAME)
    sc.add_argument('--topic', action='store', help=TOPIC_NAME)

    p.add_argument('--max-count', action='store', type=int,
                   required='--peek' in sys.argv,
                   default=0, help='Maximum message count')


def tool_download(args: argparse.Namespace,
                  parser: argparse.ArgumentParser):
    if args.queue:
        if args.peek:
            _tool_peek_queue(args, parser)
        else:
            _tool_download_queue(args, parser)
    elif args.topic:
        _tool_download_topic(args, parser)


def _tool_download_queue(args: argparse.Namespace,
                         parser: argparse.ArgumentParser):
    connection, err = parse_conection_profile(args, parser)
    if err:
        parser.exit(1, str(err))

    output = _get_output(args.queue, args.output, args.dead_letter)
    dlq = args.dead_letter

    sub_queue = None if not dlq else ServiceBusSubQueue.DEAD_LETTER
    max_receive = args.max_count or None
    max_timeout = args.timeout or None
    file_prefix = args.file_prefix or ''
    get_console().info('Receiving from queue %s to folder %s',
                       args.queue, output)
    with ServiceBusClient.from_connection_string(connection) as client:

        with client.get_queue_receiver(
                args.queue,
                sub_queue=sub_queue) as receiver:

            count = 0
            do_again = True
            while do_again:
                received = 0
                for message in receiver.receive_messages(
                        max_message_count=max_receive,
                        max_wait_time=max_timeout):
                    received += 1
                    body = next(message.body)
                    ext = _get_extension(body)
                    file_name = os.path.join(
                        output, "{0}{1}_{2}{3}".format(
                            file_prefix,
                            message.enqueued_time_utc.strftime(
                                "%Y%m%d_%H%M%S"),
                            message.message_id,
                            ext))
                    with open(file_name, 'bw') as f:
                        f.write(body)

                    receiver.complete_message(message)
                    get_console().info('Received #%s -> %s',
                                       message.message_id, file_name)

                count += received
                if received == 0 or (max_receive and count >= max_receive):
                    do_again = False
            get_console().info('Received %s messages', count)


def _tool_peek_queue(args: argparse.Namespace,
                     parser: argparse.ArgumentParser):
    connection, err = parse_conection_profile(args, parser)
    if err:
        parser.exit(1, str(err))

    output = _get_output(args.queue, args.output, args.dead_letter)
    dlq = args.dead_letter

    sub_queue = None if not dlq else ServiceBusSubQueue.DEAD_LETTER
    if args.max_count < 1:
        parser.exit(1, '--max-count argument must be a positive number')

    max_timeout = args.timeout or None
    file_prefix = args.file_prefix or ''
    get_console().info('Peeking from queue %s to folder %s',
                       args.queue, output)
    with ServiceBusClient.from_connection_string(connection) as client:

        with client.get_queue_receiver(
                args.queue,
                sub_queue=sub_queue) as receiver:

            count = 0
            do_again = True
            while do_again:
                received = 0
                for message in receiver.peek_messages(
                        max_message_count=args.max_count,
                        max_wait_time=max_timeout):
                    received += 1
                    body = next(message.body)
                    ext = _get_extension(body)
                    file_name = os.path.join(
                        output, "{0}{1}_{2}{3}".format(
                            file_prefix,
                            message.enqueued_time_utc.strftime(
                                "%Y%m%d_%H%M%S"),
                            message.message_id,
                            ext))
                    with open(file_name, 'bw') as f:
                        f.write(body)

                    get_console().info('Peeked #%s -> %s',
                                       message.message_id, file_name)

                count += received
                if received == 0 or (args.max_count and
                                     count >= args.max_count):
                    do_again = False
            parser.exit(0, f'Peeked {count} messages')


def _tool_download_topic(args: argparse.Namespace,
                         parser: argparse.ArgumentParser):
    # TODO: Implementar download de tópicos
    raise NotImplementedError("tool_download_topic")


def _get_output(source, output_name, dlq):
    output = output_name or source
    if not output:
        raise argparse.ArgumentError('output', 'Invalid output')
    if '*' in output or '?' in output:
        raise argparse.ArgumentError(
            'output', 'Invalid output: masked (?,*) is not allowed')
    output = os.path.abspath(output)
    if dlq and not output_name:
        output = os.path.join(output, ServiceBusSubQueue.DEAD_LETTER)
    os.makedirs(output, exist_ok=True)
    return output


def _get_extension(content: bytes):
    str_content = content.decode('utf-8')
    try:
        _ = json.loads(str_content)
        return '.json'
    except json.JSONDecodeError:
        pass
    try:
        _ = xmltodict.parse(str_content)
        return '.xml'
    except Exception:
        return '.txt'
