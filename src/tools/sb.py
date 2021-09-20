class ServiceBusConnectionString:

    __slots__ = ['endpoint', 'shared_access_key_name', 'shared_access_key']

    def __init__(self, connection_string: str):
        cs_data = {}
        for data in connection_string.split(';'):
            words = data.split('=', 2)
            if len(words) > 1:
                cs_data[words[0].lower()] = words[1]

        for key in ['Endpoint', 'SharedAccessKeyName', 'SharedAccessKey']:
            value = cs_data.get(key.lower())
            if not value:
                raise ValueError(
                    'Missing endpoint value for connection string', key)
            setattr(self, to_snake_case(key), value)

    def __str__(self):
        return f"Endpoint={self.endpoint}"

    def to_string(self) -> str:
        return "Endpoint={0};SharedAccessKeyName={1};SharedAccessKey={2}".\
            format(
                self.endpoint,
                self.shared_access_key_name,
                self.shared_access_key
            )


def to_snake_case(s: str) -> str:
    r = ''
    for c in s:
        if c.isupper() and r:
            r += '_'
        r += c.lower()
    return r


def validate_queue_name(queue_name: str, allow_mask: bool) -> bool:
    valid_chars = [chr(n) for n in range(ord('a'), ord('z')+1)] +\
        [chr(n) for n in range(ord('0'), ord('9')+1)] +\
        ['_']
    if allow_mask:
        valid_chars += ['*', '?']
    for c in queue_name:
        if c not in valid_chars:
            return False
    return True
