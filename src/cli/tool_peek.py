def tool_peek(args):
    if args.queue:
        _tool_peek_queue(args)
    elif args.topic:
        _tool_peek_topic(args)


def _tool_peek_queue(args):
    # TODO: Implementar tool peek queue
    raise NotImplementedError("tool_peek_queue")


def _tool_peek_topic(args):
    # TODO: Implementar tool peek topic
    raise NotImplementedError("tool_peek_topic")
