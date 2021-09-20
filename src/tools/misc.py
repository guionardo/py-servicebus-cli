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
    bulk = []
    for item in items:
        if len(bulk) < bulk_size:
            bulk.append(item)
            continue
        bulks.append(bulk)
        bulk.clear()
    if len(bulk) > 0:
        bulks.append(bulk)
    return bulks
