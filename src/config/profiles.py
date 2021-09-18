from ._cipher import _Cipher


class ProfilesConfig():

    def __init__(self, data: dict, cipher: _Cipher) -> None:
        self._cipher = cipher
        items = data.get('items', {})
        self._data = {
            name: self._cipher.decrypt(items[name])
            for name in items.keys()
        }
        self.default: str = data.get('default', '')

    def to_dict(self) -> dict:
        return dict(
            default=self.default,
            items={
                name: self._cipher.encrypt(self._data[name])
                for name in self._data.keys()}
        )

    def set_default(self, default_profile: str) -> bool:
        if default_profile in self._data.keys():
            self.default = default_profile
        elif not default_profile:
            self.default = ''
        else:
            return False
        return True

    def __getitem__(self, key):
        return self._data.get(key, '')

    def __setitem__(self, key, value):
        if key:
            if value:
                self._data[key] = value
            else:
                self._data.pop(key, None)

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        self.current = -1
        self._keys = list(self._data.keys())
        return self

    def __next__(self):
        self.current += 1
        if self.current < len(self._data):
            return self._keys[self.current]
        raise StopIteration

    def __contains__(self, item) -> bool:
        return item in self._data.keys()
