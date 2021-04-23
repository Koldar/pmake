from collections import UserDict
from typing import Any, Tuple, Iterable


class AttrDict(object):

    def __init__(self, d):
        self.__d = d

    def __getattr__(self, item: str):
        try:
            return self.__dict__[item]
        except KeyError:
            try:
                return getattr(type(self), item).__get__(self)
            except AttributeError:
                return self.__d[item]

    def __setattr__(self, key: str, value):
        try:
            getattr(type(self), key).__set__(self, value)
        except AttributeError:
            try:
                self.__dict__[key] = value
            except KeyError:
                self.__d[key] = value

    __getitem__ = __getattr__
    __setitem__ = __setattr__

    def __contains__(self, item) -> bool:
        return item in self.__d

    def __len__(self) -> int:
        return len(self.__d)

    def items(self) -> Iterable[Tuple[int, Any]]:
        yield from self.__d.items()

    def keys(self) -> Iterable[str]:
        yield from self.__d.keys()

    def values(self) -> Iterable[Any]:
        yield from self.__d.values()

    def has_key(self, item: str) -> bool:
        return item in self