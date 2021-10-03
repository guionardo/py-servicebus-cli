def remove_quotes(s: str) -> str:
    if not isinstance(s, str):
        return s
    for q in '\'"':
        if s.startswith(q):
            s = s[1:]
        if s.endswith(q):
            s = s[0:-1]
    return s


def get_bulks(items: list, bulk_size: int) -> list:
    bulks = []
    _items = items.copy()
    while _items:
        bulks.append(_items[0:bulk_size].copy())
        _items = _items[bulk_size:]
    return bulks
