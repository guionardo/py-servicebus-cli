def remove_quotes(s: str) -> str:
    if not isinstance(s, str):
        return s
    for q in '\'"':
        if s.startswith(q):
            s = s[1:]
        if s.endswith(q):
            s = s[0:-1]
    return s
