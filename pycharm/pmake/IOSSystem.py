import abc
from typing import Union, List, Tuple, Dict, Any

import semver

from pmake.InterestingPath import InterestingPath


class IOSSystem(abc.ABC):

    @abc.abstractmethod
    def _fetch_interesting_paths(self, script: "SessionScript") -> Dict[str, List[InterestingPath]]:
        """
        Fetch all the interesting paths relative to a operating system.
        Highly dependent on the operating system. Each path has associated different actual paths, since a single

        :param script: object used to interact with the system (if you need commands to fetch the paths)

        :return:
        """
        pass

    @abc.abstractmethod
    def get_current_username(self) -> str:
        pass

    @abc.abstractmethod
    def execute(self, command: Union[str, List[str]], cwd: str = None, use_shell: bool = True,
                      capture_stdout: bool = True) -> Tuple[int, str, str]:
        pass

    @abc.abstractmethod
    def execute_admin(self, command: Union[str, List[str]], cwd: str = None, use_shell: bool = True, capture_stdout: bool = True) -> Tuple[int, str, str]:
        pass

    def _get_semantic_version(self, s: str) -> semver.VersionInfo:
        if len(s.split(".")) == 1:
            return semver.VersionInfo.parse(f"{s}.0.0")
        elif len(s.split(".")) == 2:
            return semver.VersionInfo.parse(f"{s}.0")
        else:
            return semver.VersionInfo.parse(s)

    def _fetch_latest_paths(self, script: "SessionScript", interesting_paths: Dict[str, List[InterestingPath]]) -> Dict[str, InterestingPath]:
        """
        geenrate the latest interesting paths
        :param script:
        :return:
        """

        result = {}

        architecture = script.get_architecture()

        for k, values in interesting_paths.items():
            # remove all the paths which are not involved in the current architecture
            tmp = list(filter(lambda x: x.architecture == architecture, values))
            # fetch the path with the latest version
            max_interesting_path = None
            for x in tmp:
                if max_interesting_path is None:
                    max_interesting_path = x
                elif x.version > max_interesting_path.version:
                    max_interesting_path = x

            result[k] = max_interesting_path

        return result

    def _convert_stdout(self, stdout) -> str:
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8")
        elif isinstance(stdout, list):
            tmp = []
            for x in stdout:
                if isinstance(x, bytes):
                    tmp.append(x.decode("utf-8"))
                elif isinstance(x, str):
                    tmp.append(x)
                else:
                    raise TypeError(f"invalid stdout output type {type(x)}!")
            stdout = ''.join(tmp)
        elif isinstance(stdout, str):
            stdout = str(stdout)
        else:
            raise TypeError(f"invalid stdout output type {type(stdout)}!")

        return stdout.strip()
