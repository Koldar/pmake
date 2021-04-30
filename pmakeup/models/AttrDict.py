from collections import UserDict
from typing import Any, Tuple, Iterable


class AttrDict(object):

    def __init__(self, d):
        self._d = d

    def __getattr__(self, item: str):
        if item in ["_d"]:
            return super(AttrDict, self).__getattribute__(item)
        else:
            return super(AttrDict, self).__getattribute__("_d")[item]

    def __setattr__(self, key: str, value):
        if key in ["_d"]:
            super(AttrDict, self).__setattr__(key, value)
        else:
            self._d[key] = value

    __getitem__ = __getattr__
    __setitem__ = __setattr__

    def __contains__(self, item) -> bool:
        return item in self._d

    def __len__(self) -> int:
        return len(self._d)

    def __str__(self) -> str:
        return str(self._d)

    def items(self) -> Iterable[Tuple[int, Any]]:
        yield from self._d.items()

    def keys(self) -> Iterable[str]:
        yield from self._d.keys()

    def values(self) -> Iterable[Any]:
        yield from self._d.values()

    def has_key(self, item: str) -> bool:
        return item in self