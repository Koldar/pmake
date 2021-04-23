import abc

from semantic_version import Version


class InterestingPath(abc.ABC):
    """
    a path which which is important to you in some way.
    For example, in linux it may be the installation path of a library
    """

    def __init__(self, architecture: int, path: str, version: Version):
        self.architecture: int = architecture
        self.path: path = path
        self.version: Version = version

    def __str__(self):
        return f"{{ architecture: {self.architecture}, version: {self.version}, path: {self.path} }}"
