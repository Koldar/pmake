from typing import Callable, Iterable


class TargetDescriptor(object):

    def __init__(self, name: str, description: str, requires: Iterable[str], function: Callable[[], None]):
        self.name = name
        self.requires = list(requires)
        self.description = description
        self.function = function
