import logging
import os
import subprocess
import tempfile
from typing import Union, List, Tuple, Dict, Any, Optional, Iterable

from semantic_version import Version

import pmakeup as pm


class WindowsOSSystem(pm.IOSSystem):

    def _write_cmd_bat_file(self, filepath: pm.path, actual_env: Dict[str, str], commands: List[Union[str, List[str]]]):
        """
        Write a bat file containing the script to execute
        """
        with open(filepath, "w") as f:
            f.write("@echo off\n")
            f.write("\n")
            # set environment variables
            for k, v in actual_env.items():
                f.write(f"set {k}={v}\n")
            # put the commands in the temp file
            for cmd in commands:
                if isinstance(cmd, str):
                    cmd_str = cmd
                elif isinstance(cmd, list):
                    cmd_str = ' '.join(cmd)
                else:
                    raise TypeError(f"Invalid type of command {type(cmd)}!")
                f.write(cmd_str)
                f.write("\n")

    def fire_command_and_wait(self, commands: List[Union[str, List[str]]], cwd: str = None, env: Dict[str, Any] = None,
                              check_exit_code: bool = True, timeout: int = None, log_entry: bool = False) -> int:
        # get cwd
        if cwd is None:
            cwd = os.getcwd()
        # fetch the current user environment variables and updates with the ones from the caller
        actual_env = dict(os.environ)
        if env is not None:
            for k, v in env.items():
                actual_env[k] = v

        # create tempfile
        with self.create_temp_directory_with("pmakeup-command-") as absolute_temp_dir:
            try:
                filepath = self.create_temp_file(directory=absolute_temp_dir, file_prefix="cmd_", file_suffix=".cmd",
                                                 executable_for_owner=True)
                self._write_cmd_bat_file(filepath, actual_env, commands)

                # Now execute file
                actual_command = f"""cmd.exe /C \"{filepath} > nul 2>&1\""""
                log_method = logging.critical if log_entry else logging.debug
                log_method(f"Executing {actual_command}")
                with open(filepath, "r") as f:
                    log_method(f"in file \"{filepath}\" = \n{f.read()}")

                if len(os.getcwd()) > 258:
                    raise ValueError(f"{os.getcwd()} path is too long. needs to be at most 258")
                if len(cwd) > 258:
                    raise ValueError(f"{cwd} path is too long. needs to be at most 258")
                result = subprocess.run(
                    args=actual_command,
                    cwd=cwd,
                    shell=True,
                    capture_output=False,
                    timeout=timeout,
                    env=actual_env
                )

                if check_exit_code and result.returncode != 0:
                    raise pm.PMakeupException(f"cwd=\"{cwd}\" command=\"{actual_command}\" exit=\"{result.returncode}\"")
                return result.returncode
            finally:
                os.unlink(filepath)

    def fire_admin_command_and_wait(self, commands: List[Union[str, List[str]]], cwd: str = None,
                                    env: Dict[str, Any] = None, check_exit_code: bool = True, timeout: int = None,
                                    log_entry: bool = False, credential_type: str = None, credential: any = None) -> int:

        # get cwd
        if cwd is None:
            cwd = os.getcwd()
        # fetch the current user environment variables and updates with the ones from the caller
        actual_env = dict(os.environ)
        if env is not None:
            for k, v in env.items():
                actual_env[k] = v

        # create tempfile
        with self.create_temp_directory_with("pmakeup-command-") as absolute_temp_dir:
            try:
                filepath = self.create_temp_file(directory=absolute_temp_dir, file_prefix="cmd_", file_suffix=".cmd", executable_for_owner=True)
                self._write_cmd_bat_file(filepath, actual_env, commands)

                # Now execute file
                if credential_type == 'password':
                    admin_password: str = credential
                    actual_command = f"""powershell.exe -Command \"Start-Process -FilePath 'cmd.exe' -ArgumentList '/C','{filepath} > nul 2>&1' -WorkingDirectory '{cwd}' -Wait -Verb RunAs\""""
                else:
                    raise ValueError(f"invalid credential type {credential_type}")

                log_method = logging.critical if log_entry else logging.debug
                log_method(f"Executing {actual_command}")
                with open(filepath, "r") as f:
                    log_method(f"in file \"{filepath}\" = \n{f.read()}")

                if len(os.getcwd()) > 258:
                    raise ValueError(f"{os.getcwd()} path is too long. needs to be at most 258")
                if len(cwd) > 258:
                    raise ValueError(f"{cwd} path is too long. needs to be at most 258")
                result = subprocess.run(
                    args=actual_command,
                    cwd=cwd,
                    shell=True,
                    capture_output=False,
                    timeout=timeout,
                    env=actual_env
                )

                if check_exit_code and result.returncode != 0:
                    raise pm.PMakeupException(f"cwd=\"{cwd}\" command=\"{actual_command}\" exit=\"{result.returncode}\"")
                return result.returncode
            finally:
                os.unlink(filepath)

    def fire_command_and_forget(self, commands: List[Union[str, List[str]]], cwd: str = None, env: Dict[str, Any] = None, log_entry: bool = False) -> int:
        # get cwd
        if cwd is None:
            cwd = os.getcwd()
        # fetch the current user environment variables and updates with the ones from the caller
        actual_env = dict(os.environ)
        if env is not None:
            for k, v in env.items():
                actual_env[k] = v

        # create tempfile
        with self.create_temp_directory_with("pmakeup-command-") as absolute_temp_dir:
            try:
                filepath = self.create_temp_file(directory=absolute_temp_dir, file_prefix="cmd_", file_suffix=".cmd",
                                                 executable_for_owner=True)
                self._write_cmd_bat_file(filepath, actual_env, commands)

                # Now execute file
                actual_command = f"""cmd.exe /C \"{filepath} > nul 2>&1\""""
                log_method = logging.critical if log_entry else logging.debug
                log_method(f"Executing {actual_command}")
                with open(filepath, "r") as f:
                    log_method(f"in file \"{filepath}\" = \n{f.read()}")

                if len(os.getcwd()) > 258:
                    raise ValueError(f"{os.getcwd()} path is too long. needs to be at most 258")
                if len(cwd) > 258:
                    raise ValueError(f"{cwd} path is too long. needs to be at most 258")
                process = subprocess.Popen(
                    args=actual_command,
                    cwd=cwd,
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    env=actual_env
                )
                return process.pid
            finally:
                os.unlink(filepath)

    def fire_admin_command_and_forget(self, commands: List[Union[str, List[str]]], cwd: str = None, env: Dict[str, Any] = None, log_entry: bool = False, credential_type: str = None, credential: any = None) -> int:
        # get cwd
        if cwd is None:
            cwd = os.getcwd()
        # fetch the current user environment variables and updates with the ones from the caller
        actual_env = dict(os.environ)
        if env is not None:
            for k, v in env.items():
                actual_env[k] = v

        # create tempfile
        with self.create_temp_directory_with("pmakeup-command-") as absolute_temp_dir:
            try:
                filepath = self.create_temp_file(directory=absolute_temp_dir, file_prefix="cmd_", file_suffix=".cmd",
                                                 executable_for_owner=True)
                self._write_cmd_bat_file(filepath, actual_env, commands)

                # Now execute file
                if credential_type == 'password':
                    admin_password: str = credential
                    actual_command = f"""powershell.exe -Command \"Start-Process -FilePath 'cmd.exe' -ArgumentList '/C','{filepath} > nul 2>&1' -WorkingDirectory '{cwd}' -Wait -Verb RunAs\""""
                else:
                    raise ValueError(f"invalid credential type {credential_type}")

                log_method = logging.critical if log_entry else logging.debug
                log_method(f"Executing {actual_command}")
                with open(filepath, "r") as f:
                    log_method(f"in file \"{filepath}\" = \n{f.read()}")

                if len(os.getcwd()) > 258:
                    raise ValueError(f"{os.getcwd()} path is too long. needs to be at most 258")
                if len(cwd) > 258:
                    raise ValueError(f"{cwd} path is too long. needs to be at most 258")
                process = subprocess.Popen(
                    args=actual_command,
                    cwd=cwd,
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    env=actual_env
                )
                return process.pid
            finally:
                os.unlink(filepath)

    def fire_command_and_show_stdout(self, commands: List[Union[str, List[str]]], cwd: str = None,
                                     env: Dict[str, Any] = None, check_exit_code: bool = True, timeout: int = None,
                                     log_entry: bool = False) -> int:

        #get cwd
        if cwd is None:
            cwd = os.getcwd()
        # fetch the current user environment variables and updates with the ones from the caller
        actual_env = dict(os.environ)
        if env is not None:
            for k, v in env.items():
                actual_env[k] = v

        # create tempfile
        with self.create_temp_directory_with("pmakeup-command-") as absolute_temp_dir:
            try:
                filepath = self.create_temp_file(directory=absolute_temp_dir, file_prefix="cmd_", file_suffix=".cmd",
                                                 executable_for_owner=True)
                self._write_cmd_bat_file(filepath, actual_env, commands)

                actual_command = f"""cmd.exe /C \"{filepath}\""""

                log_method = logging.critical if log_entry else logging.debug
                log_method(f"Executing {actual_command}")
                with open(filepath, "r") as f:
                    log_method(f"in file \"{filepath}\" = \n{f.read()}")

                if len(os.getcwd()) > 258:
                    raise ValueError(f"{os.getcwd()} path is too long. needs to be at most 258")
                if len(cwd) > 258:
                    raise ValueError(f"{cwd} path is too long. needs to be at most 258")
                result = subprocess.run(
                    args=actual_command,
                    cwd=cwd,
                    shell=True,
                    capture_output=False,
                    timeout=timeout,
                    env=actual_env
                )

                if check_exit_code and result.returncode != 0:
                    raise pm.PMakeupException(f"cwd=\"{cwd}\" command=\"{actual_command}\" exit=\"{result.returncode}\"")
                return result.returncode
            finally:
                os.unlink(filepath)

    def fire_admin_command_and_show_stdout(self, commands: List[Union[str, List[str]]], cwd: str = None,
                                           env: Dict[str, Any] = None, check_exit_code: bool = True,
                                           timeout: int = None, log_entry: bool = False, credential_type: str = None,
                                           credential: any = None) -> int:

        # get cwd
        if cwd is None:
            cwd = os.getcwd()
        # fetch the current user environment variables and updates with the ones from the caller
        actual_env = dict(os.environ)
        if env is not None:
            for k, v in env.items():
                actual_env[k] = v

        # create tempfile
        with self.create_temp_directory_with("pmakeup-command-") as absolute_temp_dir:
            try:
                filepath = self.create_temp_file(directory=absolute_temp_dir, file_prefix="cmd_", file_suffix=".cmd",
                                                 executable_for_owner=True)
                self._write_cmd_bat_file(filepath, actual_env, commands)

                # Now execute file
                if credential_type == "password":
                    actual_command = f"""powershell.exe -Command \"Start-Process -FilePath 'cmd.exe' -ArgumentList '/C','{filepath}' -WorkingDirectory '{cwd}' -Wait -Verb RunAs\""""
                else:
                    raise ValueError(f"invalid credential type {credential_type}")

                log_method = logging.critical if log_entry else logging.debug
                log_method(f"Executing {actual_command}")
                with open(filepath, "r") as f:
                    log_method(f"in file \"{filepath}\" = \n{f.read()}")

                if len(os.getcwd()) > 258:
                    raise ValueError(f"{os.getcwd()} path is too long. needs to be at most 258")
                if len(cwd) > 258:
                    raise ValueError(f"{cwd} path is too long. needs to be at most 258")
                result = subprocess.run(
                    args=actual_command,
                    cwd=cwd,
                    shell=True,
                    capture_output=False,
                    timeout=timeout,
                    env=actual_env
                )

                if check_exit_code and result.returncode != 0:
                    raise pm.PMakeupException(f"cwd=\"{cwd}\" command=\"{actual_command}\" exit=\"{result.returncode}\"")
                return result.returncode
            finally:
                os.unlink(filepath)

    def fire_command_and_capture_stdout(self, commands: List[Union[str, List[str]]], cwd: str = None,
                                        env: Dict[str, Any] = None, check_exit_code: bool = True, timeout: int = None,
                                        log_entry: bool = False) -> Tuple[int, str, str]:
        # get cwd
        if cwd is None:
            cwd = os.getcwd()
        # fetch the current user environment variables and updates with the ones from the caller
        actual_env = dict(os.environ)
        if env is not None:
            for k, v in env.items():
                actual_env[k] = v

        # create tempfile
        with self.create_temp_directory_with("pmakeup-command-") as absolute_temp_dir:
            try:
                filepath = self.create_temp_file(directory=absolute_temp_dir, file_prefix="cmd_", file_suffix=".cmd", executable_for_owner=True)
                self._write_cmd_bat_file(filepath, actual_env, commands)
                stdout_filepath = os.path.join(absolute_temp_dir, "stdout.txt")
                stderr_filepath = os.path.join(absolute_temp_dir, "stderr.txt")

                # Now execute file

                actual_command = f"""cmd.exe /C \"{filepath} 1> {stdout_filepath} 2> {stderr_filepath}\""""
                actual_capture_output = False
                actual_read_stdout = True

                log_method = logging.critical if log_entry else logging.debug
                log_method(f"Executing {actual_command}")
                with open(filepath, "r") as f:
                    log_method(f"in file \"{filepath}\" = \n{f.read()}")

                if len(os.getcwd()) > 258:
                    raise ValueError(f"{os.getcwd()} path is too long. needs to be at most 258")
                if len(cwd) > 258:
                    raise ValueError(f"{cwd} path is too long. needs to be at most 258")
                result = subprocess.run(
                    args=actual_command,
                    cwd=cwd,
                    shell=True,
                    capture_output=False,
                    timeout=timeout,
                    env=actual_env
                )

                if check_exit_code and result.returncode != 0:
                    raise pm.PMakeupException(f"cwd=\"{cwd}\" command=\"{actual_command}\" exit=\"{result.returncode}\"")

                with open(stdout_filepath) as f:
                    stdout = self._convert_stdout(f.read())
                with open(stderr_filepath) as f:
                    stderr = self._convert_stdout(f.read())

                return result.returncode, stdout, stderr
            finally:
                os.unlink(filepath)

    def fire_admin_command_and_capture_stdout(self, commands: List[Union[str, List[str]]], cwd: str = None,
                                              env: Dict[str, Any] = None, check_exit_code: bool = True,
                                              timeout: int = None, log_entry: bool = False, credential_type: str = None,
                                              credential: any = None) -> Tuple[int, str, str]:
        # get cwd
        if cwd is None:
            cwd = os.getcwd()
        # fetch the current user environment variables and updates with the ones from the caller
        actual_env = dict(os.environ)
        if env is not None:
            for k, v in env.items():
                actual_env[k] = v

        # create tempfile
        with self.create_temp_directory_with("pmakeup-command-") as absolute_temp_dir:
            try:
                filepath = self.create_temp_file(directory=absolute_temp_dir, file_prefix="cmd_", file_suffix=".cmd", executable_for_owner=True)
                self._write_cmd_bat_file(filepath, actual_env, commands)

                stdout_filepath = os.path.join(absolute_temp_dir, "stdout.txt")
                stderr_filepath = os.path.join(absolute_temp_dir, "stderr.txt")

                # Now execute file
                if credential_type == "password":
                    actual_command = f"""powershell.exe -Command \"Start-Process -FilePath 'cmd.exe' -ArgumentList '/C','{filepath} 1> {stdout_filepath} 2> {stderr_filepath}' -WorkingDirectory '{cwd}' -Wait -Verb RunAs\""""
                else:
                    raise ValueError(f"invlid credential type {credential_type}")

                log_method = logging.critical if log_entry else logging.debug
                log_method(f"Executing {actual_command}")
                with open(filepath, "r") as f:
                    log_method(f"in file \"{filepath}\" = \n{f.read()}")

                if len(os.getcwd()) > 258:
                    raise ValueError(f"{os.getcwd()} path is too long. needs to be at most 258")
                if len(cwd) > 258:
                    raise ValueError(f"{cwd} path is too long. needs to be at most 258")
                result = subprocess.run(
                    args=actual_command,
                    cwd=cwd,
                    shell=True,
                    capture_output=False,
                    timeout=timeout,
                    env=actual_env
                )

                if check_exit_code and result.returncode != 0:
                    raise pm.PMakeupException(f"cwd=\"{cwd}\" command=\"{actual_command}\" exit=\"{result.returncode}\"")

                with open(stdout_filepath) as f:
                    stdout = self._convert_stdout(f.read())
                with open(stderr_filepath) as f:
                    stderr = self._convert_stdout(f.read())

                return result.returncode, stdout, stderr
            finally:
                os.unlink(filepath)

    def __init__(self, model):
        self._model: "pm.PMakeupModel" = model

    def get_program_path(self) -> Iterable[pm.path]:
        return os.environ["PATH"].split(os.pathsep)

    def find_executable_in_program_directories(self, program_name: str) -> Optional[pm.path]:
        # we first search in program files and only then fallbacks to path.
        for root in [r"C:\Program Files", r"C:\Program Files (x86)"] + list(self.get_program_path()):
            for f in self._model.get_files_plugin().find_file(root_folder=root, filename=program_name):
                return f
        else:
            return None

    def set_global_environment_variable(self, group_name: str, name: str, value: Any):
        self.fire_command_and_capture_stdout(commands=[
                f"""setx /M "{name}" "{value}" """
            ],
        )

    def get_env_variable(self, name: str) -> str:
        code, stdout, _ = self.fire_command_and_capture_stdout(
            commands=[f"echo %{name}%"],
            log_entry=True,
        )

        stdout = stdout.strip()
        if len(stdout) == 0:
            raise pm.PMakeupException(f"Cannot find the environment variable \"{name}\" for user \"{self.get_current_username()}\"")

        return stdout

    def get_home_folder(self) -> pm.path:
        return self.get_env_variable("USERPROFILE")

    def fetch_interesting_paths(self, model: "pm.PMakeupModel") -> Dict[str, List[pm.InterestingPath]]:
        # <Regasm32>C:\Windows\Microsoft.NET\Framework\v4.0.30319\RegAsm.exe</Regasm32>
        # <Regasm64>C:\Windows\Microsoft.NET\Framework64\v4.0.30319\RegAsm.exe</Regasm64>
        # fetch regasm

        interesting_paths = {}
        architecture = self._model.get_core_plugin().get_architecture()

        # REGASM
        folder32 = os.path.join(r"C:\\", "Windows", "Microsoft.NET", "Framework")
        folder64 = os.path.join(r"C:\\", "Windows", "Microsoft.NET", "Framework64")

        if "regasm" not in interesting_paths:
            interesting_paths["regasm"] = []

        if os.path.isdir(folder32):
            # subfolder ris something like v1.2.3
            for subfolder in self._model.get_files_plugin().ls_only_directories(folder32):
                interesting_paths["regasm"].append(pm.InterestingPath(
                    architecture=32,
                    path=self._model.get_core_plugin()._abs_wrt_cwd(folder32, subfolder, "RegAsm.exe"),
                    version=self._get_semantic_version(subfolder[1:])
                ))

        if os.path.isdir(folder64):
            # subfolder ris something like v1.2.3
            for subfolder in self._model.get_files_plugin().ls_only_directories(folder64):
                interesting_paths["regasm"].append(pm.InterestingPath(
                    architecture=64,
                    path=self._model.get_core_plugin()._abs_wrt_cwd(folder64, subfolder, "RegAsm.exe"),
                    version=self._get_semantic_version(subfolder[1:])
                ))

        # INTERNET EXPLORER AND OTHER COMMON PROGRAMS ON WINDOWS

        # iexplorer_path = script.read_registry_local_machine_value
        # ("Computer\HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\IEXPLORE.EXE", "")
        iexplorer_path = os.path.abspath(os.path.join("C:\\", "Program Files", "Internet Explorer", "iexplore.exe"))
        interesting_paths["internet-explorer"] = []
        interesting_paths["internet-explorer"].append(pm.InterestingPath(
            architecture=self._model.get_core_plugin().get_architecture(),
            path=iexplorer_path,
            version=Version("1.0.0")
        ))

        # Computer\HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\IEXPLORE.EXE

        return interesting_paths

    def is_program_installed(self, program_name: str) -> bool:
        exit_code, _, _ = self.fire_command_and_capture_stdout(
            commands=[f"where {program_name}"],
            check_exit_code=False
        )
        return exit_code == 0
