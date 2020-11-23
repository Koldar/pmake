import abc

import semver


class InterestingPath(abc.ABC):

    def __init__(self, architecture: int, path: str, version: semver.VersionInfo):
        self.architecture: int = architecture
        self.path: path = path
        self.version: semver.VersionInfo = version

    def __str__(self):
        return f"{{ architecture: {self.architecture}, version: {self.version}, path: {self.path} }}"
