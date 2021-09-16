import glob
import logging
import os
from typing import List

from azure.servicebus import ServiceBusClient, ServiceBusMessage


def tool_upload(args):
    if args.queue:
        _tool_upload_queue(args)
    elif args.topic:
        _tool_upload_topic(args)


def _tool_upload_queue(args):
    files = _get_source(args.source)
    console = logging.getLogger('console')
    if not files:
        console.info(
            'There are no files to upload at %s', args.source)
        return
    max_files = len(files) if args.max_count <= 0 else args.max_count
    files = [file for file in files if os.path.isfile(
        file) and not os.path.isdir(file)][0:max_files]
    messages = []
    bulk_size = 10
    sent_files = []
    sending_files = []
    console.info('Uploading files from %s to queue %s',
                 args.source, args.queue)
    with ServiceBusClient.from_connection_string(args.connection) as client:
        with client.get_queue_sender(args.queue) as sender:
            while files:
                if len(sent_files) >= max_files:
                    break

                file = files.pop(0)

                with open(file, 'br') as f:
                    raw_message = ServiceBusMessage(f.read())
                messages.append(raw_message)
                sending_files.append(file)
                if len(messages) >= bulk_size:
                    try:
                        sender.send_messages(messages)
                        messages.clear()
                        for f in sending_files:
                            console.info('Sent %s', f)
                        _move_files(sending_files, 'sent')
                        sending_files.clear()
                    except Exception as exc:
                        messages.clear()
                        console.error('Failed to send files: %s', exc)
                        break

            if messages:
                try:
                    sender.send_messages(messages)

                    for f in sending_files:
                        console.info('Sent %s', f)

                except Exception as exc:

                    console.error('Failed to send files: %s', exc)

            _move_files(sending_files, 'sent')


def _tool_upload_topic(args):
    pass


def _get_source(source: str) -> List[str]:
    if os.path.isdir(source):
        source = os.path.join(source, '*')
    return glob.glob(source)


def _move_files(files: List[str], sub_folder: str):
    if not files:
        return
    console = logging.getLogger('console')
    new_folder = os.path.join(os.path.dirname(files[0]), sub_folder)
    os.makedirs(new_folder, exist_ok=True)
    for file in files:
        new_file = os.path.join(new_folder, os.path.basename(file))
        os.rename(file, new_file)
        console.info('Moved file %s -> %s', file, new_file)
