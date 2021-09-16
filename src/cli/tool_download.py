import json
import logging
import os
from argparse import ArgumentError

import xmltodict
from azure.servicebus import ServiceBusClient, ServiceBusSubQueue


def tool_download(args):
    if args.queue:
        _tool_download_queue(args)
    elif args.topic:
        _tool_download_topic(args)


def _tool_download_queue(args):
    log = logging.getLogger('console')
    output = _get_output(args.queue, args.output, args.dead_letter)
    dlq = args.dead_letter

    sub_queue = None if not dlq else ServiceBusSubQueue.DEAD_LETTER
    max_receive = args.max_count or None
    max_timeout = args.timeout or None
    file_prefix = args.file_prefix or ''
    log.info('Receiving from queue %s to folder %s', args.queue, output)
    with ServiceBusClient.from_connection_string(args.connection) as client:

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
                    log.info('Received #%s -> %s',
                             message.message_id, file_name)

                count += received
                if received == 0 or (max_receive and count >= max_receive):
                    do_again = False
            log.info('Received %s messages', count)


def _tool_download_topic(args):
    print('Em desenvolvimento')


def _get_output(source, output_name, dlq):
    output = output_name or source
    if not output:
        raise ArgumentError('output', 'Invalid output')
    if '*' in output or '?' in output:
        raise ArgumentError(
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
