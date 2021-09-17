def tool_peek(args):
    if args.queue:
        _tool_peek_queue(args)
    elif args.topic:
        _tool_peek_topic(args)
