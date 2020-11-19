import abc
from typing import Union, List, Tuple, Dict, Any

import semver

from pmake.InterestingPath import InterestingPath
from pmake.commons_types import path


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
                      capture_stdout: bool = True, check_output: bool = True) -> Tuple[int, str, str]:
        """
        Execute an arbitrary command

        :param command: the command to execute. Can either be a list of strnigs or a string
        :param cwd: directory where the command will be executed
        :param use_shell: parameter to pass to subprocess method
        :param capture_stdout: if true, we will save the output of the program and return it (both stdout and stderr)
        :param check_output: if true, we will generate an exception if the exit code is different than 0
        """
        pass

    @abc.abstractmethod
    def execute_admin(self, command: Union[str, List[str]], cwd: str = None, use_shell: bool = True, capture_stdout: bool = True, check_output: bool = True) -> Tuple[int, str, str]:
        """
        Execute an arbitrary command as an administrator

        :param command: the command to execute. Can either be a list of strnigs or a string
        :param cwd: directory where the command will be executed
        :param use_shell: parameter to pass to subprocess method
        :param capture_stdout: if true, we will save the output of the program and return it (both stdout and stderr)
        :param check_output: if true, we will generate an exception if the exit code is different than 0
        """
        pass

    @abc.abstractmethod
    def execute_admin_with_password(self, command: Union[str, List[str]], password: str, cwd: str = None, use_shell: bool = True, check_output: bool = True) -> str:
        """
        Execute an admin command by passing an admin password. this is **INCREDIBLY INSECURE**!!!!!!!!!!!
        Do **NOT** use it if security is concern (which is usually the case!). The command has been introduced because
        it is normally the case to compile something on your machine and just for you.

        :param command: the command to execute as admin
        :param password: the password for admin
        :param cwd: current working directory where the command is executed
        :param use_shell: if true, we will enable the "use_shell" on subprocess methods
        :return: the stdout of the command
        :param check_output: if true, we will generate an exception if the exit code is different than 0
        """
        pass

    @abc.abstractmethod
    def is_program_installed(self, program_name: str) -> bool:
        """
        Check if a program is installed on the platform.

        :param program_name: name of the program
        :return: true if the program is installed on the system, false otherwise4
        """
        pass

    @abc.abstractmethod
    def get_env_variable(self, name: str) -> str:
        """
        Get an evnironment variable value.
        We will use the current user environment to determine the variable
        Raises an exception if the variable does not exist

        :param name: the environment variable to fetch
        :return: the environmkent variable value
        """
        pass

    @abc.abstractmethod
    def get_home_folder(self) -> path:
        """
        Get the absolute home folder of the current user
        """
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
