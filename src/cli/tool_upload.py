import os
from typing import List

from azure.servicebus import ServiceBusClient, ServiceBusMessage
from src.tools.files import get_files
from src.tools.logging import get_console


def tool_upload(args):
    if args.queue:
        _tool_upload_queue(args)
    elif args.topic:
        _tool_upload_topic(args)


def _tool_upload_queue(args):
    files = get_files(args.source, args.max_count)
    if not files:
        get_console().info(
            'There are no files to upload at %s', args.source)
        return

    messages = []
    bulk_size = 10
    sending_files = []
    get_console().info('Uploading files from %s to queue %s',
                       args.source, args.queue)
    with ServiceBusClient.from_connection_string(args.connection) as client:
        with client.get_queue_sender(args.queue) as sender:
            while files:
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
                            get_console().info('Sent %s', f)
                        _move_files(sending_files, 'sent')
                        sending_files.clear()
                    except Exception as exc:
                        messages.clear()
                        get_console().error('Failed to send files: %s', exc)
                        break

            if messages:
                try:
                    sender.send_messages(messages)

                    for f in sending_files:
                        get_console().info('Sent %s', f)

                except Exception as exc:

                    get_console().error('Failed to send files: %s', exc)

            _move_files(sending_files, 'sent')


def _tool_upload_topic(args):
    raise NotImplementedError("tool_upload_topic")


def _move_files(files: List[str], sub_folder: str):
    if not files:
        return
    new_folder = os.path.join(os.path.dirname(files[0]), sub_folder)
    os.makedirs(new_folder, exist_ok=True)
    for file in files:
        new_file = os.path.join(new_folder, os.path.basename(file))
        os.rename(file, new_file)
        get_console().info('Moved file %s -> %s', file, new_file)
