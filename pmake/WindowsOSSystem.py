import logging
import os
import subprocess
import tempfile
import time
from typing import Union, List, Tuple, Dict, Any

import semver

from pmake.IOSSystem import IOSSystem
from pmake.InterestingPath import InterestingPath
from pmake.commons_types import path
from pmake.exceptions.PMakeException import PMakeException


class WindowsOSSystem(IOSSystem):

    def set_global_environment_variable(self, group_name: str, name: str, value: Any):
        self.execute_command(commands=[
                f"""setx /M "{name}" "{value}" """
            ],
            show_output_on_screen=False,
            capture_stdout=True,
        )

    def execute_command(self, commands: List[Union[str, List[str]]], show_output_on_screen: bool, capture_stdout: bool,
                        cwd: str = None, env: Dict[str, Any] = None, check_exit_code: bool = True, timeout: int = None,
                        execute_as_admin: bool = False, admin_password: str = None, log_entry: bool = False) -> Tuple[
        int, str, str]:
        # get cwd
        if cwd is None:
            cwd = os.getcwd()
        # fetch the current user environment variables and updates with the ones from the caller
        actual_env = dict(os.environ)
        if env is not None:
            for k, v in env.items():
                actual_env[k] = v

        # create tempfile
        with self.create_temp_directory_with("pmake-command-") as absolute_temp_dir:
            try:
                filepath = self.create_temp_file(directory=absolute_temp_dir, file_prefix="cmd_", file_suffix=".cmd",
                                                 executable_for_owner=True)
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

                stdout_filepath = os.path.join(absolute_temp_dir, "stdout.txt")
                stderr_filepath = os.path.join(absolute_temp_dir, "stderr.txt")

                # Now execute file
                if execute_as_admin:
                    if admin_password:
                        if show_output_on_screen and capture_stdout:
                            actual_command = f"""powershell.exe -Command \"Start-Process -FilePath 'cmd.exe' -ArgumentList '/C','{filepath}' -WorkingDirectory '{cwd}' -Wait -Verb RunAs\""""
                            actual_capture_output = True
                            actual_read_stdout = False
                        elif show_output_on_screen and not capture_stdout:
                            actual_command = f"""powershell.exe -Command \"Start-Process -FilePath 'cmd.exe' -ArgumentList '/C','{filepath}' -WorkingDirectory '{cwd}' -Wait -Verb RunAs\""""
                            actual_capture_output = False
                            actual_read_stdout = False
                        elif not show_output_on_screen and capture_stdout:
                            actual_command = f"""powershell.exe -Command \"Start-Process -FilePath 'cmd.exe' -ArgumentList '/C','{filepath} 1> {stdout_filepath} 2> {stderr_filepath}' -WorkingDirectory '{cwd}' -Wait -Verb RunAs\""""
                            actual_capture_output = False
                            actual_read_stdout = True
                        else:
                            actual_command = f"""powershell.exe -Command \"Start-Process -FilePath 'cmd.exe' -ArgumentList '/C','{filepath} > nul 2>&1' -WorkingDirectory '{cwd}' -Wait -Verb RunAs\""""
                            actual_capture_output = False
                            actual_read_stdout = False
                    else:
                        if show_output_on_screen and capture_stdout:
                            actual_command = f"""powershell.exe -Command \"Start-Process -FilePath 'cmd.exe' -ArgumentList '/C','{filepath}' -WorkingDirectory '{cwd}' -Wait -Verb RunAs\""""
                            actual_capture_output = True
                            actual_read_stdout = False
                        elif show_output_on_screen and not capture_stdout:
                            actual_command = f"""powershell.exe -Command \"Start-Process -FilePath 'cmd.exe' -ArgumentList '/C','{filepath}' -WorkingDirectory '{cwd}' -Wait -Verb RunAs\""""
                            actual_capture_output = False
                            actual_read_stdout = False
                        elif not show_output_on_screen and capture_stdout:
                            actual_command = f"""powershell.exe -Command \"Start-Process -FilePath 'cmd.exe' -ArgumentList '/C','{filepath} 1> {stdout_filepath} 2> {stderr_filepath}' -WorkingDirectory '{cwd}' -Wait -Verb RunAs\""""
                            actual_capture_output = False
                            actual_read_stdout = True
                        else:
                            actual_command = f"""powershell.exe -Command \"Start-Process -FilePath 'cmd.exe' -ArgumentList '/C','{filepath} > nul 2>&1' -WorkingDirectory '{cwd}' -Wait -Verb RunAs\""""
                            actual_capture_output = False
                            actual_read_stdout = False

                else:

                    if show_output_on_screen and capture_stdout:
                        actual_command = f"""cmd.exe /C \"{filepath}\""""
                        actual_capture_output = True
                        actual_read_stdout = False
                    elif show_output_on_screen and not capture_stdout:
                        actual_command = f"""cmd.exe /C \"{filepath}\""""
                        actual_capture_output = False
                        actual_read_stdout = False
                    elif not show_output_on_screen and capture_stdout:
                        actual_command = f"""cmd.exe /C \"{filepath} 1> {stdout_filepath} 2> {stderr_filepath}\""""
                        actual_capture_output = False
                        actual_read_stdout = True
                    else:
                        actual_command = f"""cmd.exe /C \"{filepath} > nul 2>&1\""""
                        actual_capture_output = False
                        actual_read_stdout = False

                if log_entry:
                    log_method = logging.critical
                else:
                    log_method = logging.debug
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
                    capture_output=actual_capture_output,
                    timeout=timeout,
                    env=actual_env
                )

                if check_exit_code and result.returncode != 0:
                    raise PMakeException(f"cwd=\"{cwd}\" command=\"{actual_command}\" exit=\"{result.returncode}\"")

                if actual_capture_output:
                    stdout = self._convert_stdout(result.stdout)
                    stderr = self._convert_stdout(result.stderr)
                elif actual_read_stdout:
                    with open(stdout_filepath) as f:
                        stdout = self._convert_stdout(f.read())
                    with open(stderr_filepath) as f:
                        stderr = self._convert_stdout(f.read())
                else:
                    stdout = ""
                    stderr = ""

                return result.returncode, stdout, stderr
            finally:
                os.unlink(filepath)

    def get_env_variable(self, name: str) -> str:
        code, stdout, _ = self.execute_command(
            commands=[f"echo %{name}%"],
            show_output_on_screen=False,
            capture_stdout=True,
            execute_as_admin=False,
            log_entry=True,
        )

        stdout = stdout.strip()
        if len(stdout) == 0:
            raise PMakeException(f"Cannot find the environment variable \"{name}\" for user \"{self.get_current_username()}\"")

        return stdout

    def get_home_folder(self) -> path:
        return self.get_env_variable("USERPROFILE")

    def _fetch_interesting_paths(self, script: "SessionScript.SessionScript") -> Dict[str, List[InterestingPath]]:

        # <Regasm32>C:\Windows\Microsoft.NET\Framework\v4.0.30319\RegAsm.exe</Regasm32>
        # <Regasm64>C:\Windows\Microsoft.NET\Framework64\v4.0.30319\RegAsm.exe</Regasm64>
        # fetch regasm

        interesting_paths = {}
        architecture = script.get_architecture()

        # REGASM
        folder32 = os.path.join(r"C:\\", "Windows", "Microsoft.NET", "Framework")
        folder64 = os.path.join(r"C:\\", "Windows", "Microsoft.NET", "Framework64")

        if "regasm" not in interesting_paths:
            interesting_paths["regasm"] = []

        if os.path.isdir(folder32):
            # subfolder ris something like v1.2.3
            for subfolder in script.ls_only_directories(folder32):
                interesting_paths["regasm"].append(InterestingPath(
                    architecture=32,
                    path=script.abs_wrt_cwd(folder32, subfolder, "RegAsm.exe"),
                    version=self._get_semantic_version(subfolder[1:])
                ))

        if os.path.isdir(folder64):
            # subfolder ris something like v1.2.3
            for subfolder in script.ls_only_directories(folder64):
                interesting_paths["regasm"].append(InterestingPath(
                    architecture=64,
                    path=script.abs_wrt_cwd(folder64, subfolder, "RegAsm.exe"),
                    version=self._get_semantic_version(subfolder[1:])
                ))

        # INTERNET EXPLORER AND OTHER COMMON PROGRAMS ON WINDOWS

        # iexplorer_path = script.read_registry_local_machine_value("Computer\HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\IEXPLORE.EXE", "")
        iexplorer_path = os.path.abspath(os.path.join("C:\\", "Program Files", "Internet Explorer", "iexplore.exe"))
        interesting_paths["internet-explorer"] = []
        interesting_paths["internet-explorer"].append(InterestingPath(
            architecture=script.get_architecture(),
            path=iexplorer_path,
            version=semver.VersionInfo.parse("1.0.0")
        ))

        # Computer\HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\IEXPLORE.EXE

        return interesting_paths

    # def get_current_username(self) -> str:
    #     code, stdout, stderr = self.execute_command(
    #         commands=["whoami"],
    #         capture_stdout=True,
    #         show_output_on_screen=False,
    #     )
    #     return stdout.split("\\")[1]

    def execute_admin(self, command: Union[str, List[str]], cwd: str = None, use_shell: bool = True,
                      capture_stdout: bool = True):

        stdout_filename = os.path.abspath(os.path.join(cwd, "stdout.txt"))
        stderr_filename = os.path.abspath(os.path.join(cwd, "stderr.txt"))

        if cwd is None:
            cwd = os.curdir

        if isinstance(command, str):
            cmds = command.split()
            command_name = cmds[0]
            args = ' '.join(map(lambda x: f"{x}", cmds[1:]))
        elif isinstance(command, list):
            command_name = command[0]
            args = ','.join(map(lambda x: f"'{x}'", command[1:]))
        else:
            raise TypeError(f"invalid command type {type(command)}")

        with tempfile.TemporaryDirectory(prefix="pmake_") as temp_dir:
            with tempfile.NamedTemporaryFile(delete=False, prefix="cmd_", suffix=".bat", dir=temp_dir, mode="w") as temp_bat:
                temp_bat.write(f"{command_name} {args}")
                if capture_stdout:
                    temp_bat.write(f" 2>&1 > {stdout_filename}")
                temp_bat.write("\n")
                temp_bat.flush()
                temp_filename = temp_bat.name

            returncode, stdout, stderr = self.execute(
                command=f"""powershell -Command \"Start-Process -FilePath '{temp_filename}' -WorkingDirectory '{cwd}' -Wait -Verb RunAs\"""",
                cwd=cwd,
                use_shell=use_shell,
                capture_stdout=capture_stdout
            )
            # this generates stdout and stderr
            stdout = ""
            stderr = ""
            if capture_stdout:
                if os.path.exists(stdout_filename):
                    with open(stdout_filename, "r") as f:
                        stdout = self._convert_stdout(f.read())
                if os.path.exists(stderr_filename):
                    with open(stderr_filename, "r") as f:
                        stderr = self._convert_stdout(f.read())

            return returncode, stdout, stderr

    def execute_admin_with_password(self, command: Union[str, List[str]], password: str, cwd: str = None, use_shell: bool = True) -> str:
        raise NotImplemented()

    def is_program_installed(self, program_name: str) -> bool:
        exit_code, _, _ = self.execute_command(
            commands=[f"where {program_name}"],
            show_output_on_screen=False,
            capture_stdout=False,
            check_exit_code=False
        )
        return exit_code == 0
