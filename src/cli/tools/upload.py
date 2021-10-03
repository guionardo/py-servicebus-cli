import argparse
import logging
import os
from typing import List

from azure.servicebus import ServiceBusClient, ServiceBusMessage
from src.cli.tools import (QUEUE_NAME, TOPIC_NAME, parse_conection_profile,
                           setup_connection_profile_args)
from src.tools.files import get_files
from src.tools.logging import get_console
from src.tools.misc import get_bulks
from tqdm import tqdm

MAX_FILE_SIZE = 256*1024    # Service Bus maximum message size
BULK_SIZE = 10


def setup_upload_tools(sub_comands):
    p: argparse.ArgumentParser = sub_comands.add_parser(
        'upload', help='Upload message')
    p.set_defaults(func=tool_upload)
    p.add_argument('--source', action='store',
                   help='Source files (you can use mask)', required=True)
    p.add_argument('--max-count', action='store', type=int,
                   default=0, help='Maximum message count')
    sc = p.add_mutually_exclusive_group(required=True)
    sc.add_argument('--queue', action='store', help=QUEUE_NAME)
    sc.add_argument('--topic', action='store', help=TOPIC_NAME)

    sm = p.add_mutually_exclusive_group(required=False)
    sm.add_argument('--no-move-sent', action='store_true',
                    help='No move sent files to ./sent folder')
    sm.add_argument('--move-sent', action='store',
                    default='{source}/sent', metavar='FOLDER',
                    help='Move to folder after sucessfull sending')
    setup_connection_profile_args(p)


def tool_upload(args: argparse.Namespace,
                parser: argparse.ArgumentParser):
    if args.queue:
        _tool_upload_queue(args, parser)
    elif args.topic:
        _tool_upload_topic(args, parser)


def _tool_upload_queue(args: argparse.Namespace,
                       parser: argparse.ArgumentParser):
    connection, err = parse_conection_profile(args, parser)
    if err:
        parser.exit(1, str(err))
    files = get_files(args.source, args.max_count)
    if not files:
        parser.exit(1, f'There are no files to upload at {args.source}')

    messages = []
    sending_files = []
    get_console().info('Uploading files from %s to queue %s',
                       args.source, args.queue)

    viable_files = []
    for file in files:
        f_size = os.path.getsize(file)
        if f_size > MAX_FILE_SIZE:
            get_console().info(
                'SKIPPED: File %s has %s bytes (SB limit = %s)',
                file, f_size, MAX_FILE_SIZE)
            continue
        viable_files.append(file)

    bulks = get_bulks(viable_files, BULK_SIZE)
    if not bulks:
        parser.exit(1, f'There are no viable files to upload at {args.source}')

    sent_files = []
    with ServiceBusClient.from_connection_string(connection) as client:
        with client.get_queue_sender(args.queue) as sender:
            with tqdm(total=len(viable_files),
                      desc='Uploading',
                      unit='msg') as pbar:
                for bulk in bulks:
                    for file in bulk:
                        with open(file, 'br') as f:
                            raw_message = ServiceBusMessage(f.read())
                        messages.append(raw_message)
                        sending_files.append(file)
                    try:
                        sender.send_messages(messages)
                        pbar.update(len(messages))
                        messages.clear()
                        _move_files(sending_files, args)
                        sent_files.extend(sending_files)
                        sending_files.clear()
                    except Exception as exc:
                        parser.exit(1, f'Failed to send messages: {exc}')
    if not sent_files:
        get_console().info('No files was sent')
    else:
        get_console().info(
            'Sent %s', [os.path.basename(f)
                        for f in sent_files])


def _tool_upload_topic(args: argparse.Namespace,
                       parser: argparse.ArgumentParser):
    connection, err = parse_conection_profile(args, parser)
    if err:
        parser.exit(1, str(err))

    raise NotImplementedError("tool_upload_topic")


def _move_files(files: List[str], args: argparse.Namespace):
    log = logging.getLogger(__name__)
    if not files:
        # log.info('No files to move')
        return

    if args.no_move_sent:
        # log.info('Not moving files due --no-move-sent argument')
        return

    move_sent_folder = args.move_sent
    origin_folder = os.path.dirname(files[0])
    if '{source}' in move_sent_folder:
        move_sent_folder = move_sent_folder.replace('{source}', origin_folder)

    exc = None
    try:
        con_log = []
        os.makedirs(move_sent_folder, exist_ok=True)

        for file in files:
            new_file = os.path.join(move_sent_folder, os.path.basename(file))
            os.rename(file, new_file)
            con_log.append(os.path.basename(file))
            # log.info('MOVED: %s -> %s', file, new_file)
    except Exception as exc:
        log.error('Exception when moving files: %s', exc)
    finally:
        pass
        # get_console().info('Moved files %s/ %s -> %s',
        #                    origin_folder, con_log, move_sent_folder)
    if exc:
        raise exc
