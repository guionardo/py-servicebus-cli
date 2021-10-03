import argparse
import csv
import json
import os
import sys

import xmltodict
from azure.servicebus import ServiceBusClient, ServiceBusSubQueue
from azure.servicebus._common.message import ServiceBusReceivedMessage
from src.cli.tools import (QUEUE_NAME, TOPIC_NAME, parse_conection_profile,
                           setup_connection_profile_args)
from src.tools.logging import get_console
from src.tools.service_bus.queue_info import QueueInfo
from tqdm import tqdm


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
    p.add_argument('--no-props', action='store_true', default=False,
                   help='Ignore creation of property file for each message')
    setup_connection_profile_args(p)


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
    progress_max_count = max_receive
    if not progress_max_count:
        queue_info = QueueInfo(connection, args.queue)
        if args.dead_letter:
            progress_max_count = queue_info.dead_letter_message_count
        else:
            progress_max_count = queue_info.active_message_count

    downloaded = []
    total_received = 0
    with ServiceBusClient.from_connection_string(connection) as client:

        with client.get_queue_receiver(
                args.queue,
                sub_queue=sub_queue,
                prefetch_count=10) as receiver:
            with tqdm(total=progress_max_count,
                      desc='Receiving'+(' DLQ' if args.dead_letter else ''),
                      unit='msg') as pbar:

                count = 0
                do_again = True
                while do_again:
                    received = 0
                    for message in receiver.receive_messages(
                            max_message_count=max_receive,
                            max_wait_time=max_timeout):
                        received += 1
                        total_received += 1
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

                        if not args.no_props:
                            _save_message_properties(message, file_name)

                        receiver.complete_message(message)
                        if total_received > pbar.total:
                            pbar.total = total_received
                            pbar.refresh()
                        pbar.update(1)
                        downloaded.append((message.message_id, file_name))

                    count += received
                    if received == 0 or (max_receive and count >= max_receive):
                        do_again = False

    if not downloaded:
        get_console().info('No messages received')
    else:
        for (message_id, file_name) in downloaded:
            get_console().info('%s -> %s', message_id, file_name)


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
                    ext = _get_extension(body, message._encoding)
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


def _get_extension(content: bytes, message_encoding='utf-8'):
    str_content = None
    encodings = set(['utf-8', 'ascii'])
    encodings.add(message_encoding)
    for encoding in encodings:
        try:
            str_content = content.decode(encoding)
            break
        except UnicodeDecodeError:
            get_console().warning('Failed on decoding %s', encoding)

    if not str_content:
        # get_console().info('Assuming binary data')
        return '.bin'

    if _try_parse_json(str_content):
        # get_console().info('Detected JSON content')
        return '.json'

    if _try_parse_xml(str_content):
        # get_console().info('Detected XML content')
        return '.xml'

    if _try_parse_csv(str_content):
        # get_console().info('Detected CSV content')
        return '.csv'

    # get_console().info('Detected TEXT content')
    return '.txt'


def _try_parse_json(content):
    try:
        _ = json.loads(content)
        return '.json'
    except json.JSONDecodeError:
        return None


def _try_parse_xml(content: str):
    try:
        _ = xmltodict.parse(content)
        return '.xml'
    except Exception:
        return None


def _try_parse_csv(content: str):
    try:
        lines = content.splitlines()
        reader = csv.reader(lines)
        row_count = 0
        col_count = 0
        for row in reader:
            row_count += 1
            col_count = max(len(row), col_count)

        if row_count > 0 and col_count > 1:
            return '.csv'
    except Exception:
        return None


def _save_message_properties(message: ServiceBusReceivedMessage,
                             file_name: str):
    prop_file, _ = os.path.splitext(file_name)
    prop_file += '.props'
    custom = message.application_properties or {}

    def validate_str(v):
        return v if not isinstance(v, bytes) else v.decode('ascii')
    props = dict(
        id=message.message_id,
        content_type=message.content_type,
        custom_properties={validate_str(key): validate_str(custom.get(key))
                           for key in custom.keys()},
        enqueued_time=message.enqueued_time_utc
    )
    with open(prop_file, 'w') as f:
        f.write(json.dumps(props, default=str))
