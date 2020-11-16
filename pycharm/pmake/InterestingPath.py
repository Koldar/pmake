import abc

import semver


class InterestingPath(abc.ABC):

    def __init__(self, architecture: int, path: str, version: semver.VersionInfo):
        self.architecture: int = architecture
        self.path: path = path
        self.version: semver.VersionInfo = version
