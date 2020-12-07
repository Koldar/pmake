import logging
import os
import subprocess
from typing import Union, List, Tuple, Dict, Any, Optional, Iterable

from pmake.IOSSystem import IOSSystem
from pmake.InterestingPath import InterestingPath
from pmake.commons_types import path
from pmake.exceptions.PMakeException import PMakeException


class LinuxOSSystem(IOSSystem):

    def __init__(self, model: "PMakeModel.PMakeMode"):
        super().__init__(model)

    def get_git_commit(self, p: path) -> str:
        result, stdout, stderr = self.execute_command(
            commands=[["git", "rev-parse", "HEAD"]],
            show_output_on_screen=False,
            capture_stdout=True,
            cwd=p,
        )
        return stdout

    def get_git_branch(self, p: path) -> str:
        result, stdout, stderr = self.execute_command(
            commands=[["git", "branch", "--show-current"]],
            show_output_on_screen=False,
            capture_stdout=True,
            cwd=p,
        )
        return stdout

    def get_program_path(self) -> Iterable[path]:
        return os.environ["PATH"].split(os.pathsep)

    def find_executable_in_program_directories(self, program_name: str, script: "SessionScript.SessionScript") -> Optional[path]:
        for root in list(self.get_program_path()) + [r"/opt"]:
            for f in script.find_file(root_folder=root, filename=program_name):
                return f
        else:
            return None

    def execute_command(self, commands: List[Union[str, List[str]]], show_output_on_screen: bool, capture_stdout: bool,
                        cwd: str = None, env: Dict[str, Any] = None, check_exit_code: bool = True, timeout: int = None,
                        execute_as_admin: bool = False, admin_password: str = None,
                        log_entry: bool = False) -> Tuple[int, str, str]:

        # fetch the current user environment variables and updates with the ones from the caller
        actual_env = dict(os.environ)
        if env is None:
            env = {}
        for k, v in env.items():
            actual_env[k] = v

        # create tempfile
        with self.create_temp_directory_with("pmake-command-") as absolute_temp_dir:
            filepath = self.create_temp_file(directory=absolute_temp_dir, file_prefix="cmd_", file_suffix=".bash", executable_for_owner=True)
            with open(filepath, "w") as f:
                # put the commands in the temp file
                f.write("#!/bin/bash\n")

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

            if len(actual_env) > 0:
                env_part = ','.join(actual_env.keys())
                env_part = f"--preserve-env={env_part}"
            else:
                env_part = ""

            # Now execute file
            if execute_as_admin:
                if admin_password:
                    password_file = self.create_temp_file(directory=absolute_temp_dir, file_prefix="stdin-")
                    with open(password_file, "w") as f:
                        f.write(f"{admin_password}\n")

                    if show_output_on_screen and capture_stdout:
                        actual_command = f"""cat '{password_file}' | sudo {env_part} --stdin --login bash '{filepath}'"""
                        actual_capture_output = True
                        actual_read_stdout = False
                    elif show_output_on_screen and not capture_stdout:
                        actual_command = f"""cat '{password_file}' | sudo {env_part} --stdin --login bash '{filepath}'"""
                        actual_capture_output = False
                        actual_read_stdout = False
                    elif not show_output_on_screen and capture_stdout:
                        actual_command = f"""cat '{password_file}' | sudo {env_part} --stdin --login bash '{filepath}' > {stdout_filepath} 2>{stderr_filepath}"""
                        actual_capture_output = False
                        actual_read_stdout = True
                    else:
                        actual_command = f"""cat '{password_file}' | sudo {env_part} --stdin --login bash '{filepath}' 2>&1 > /dev/null"""
                        actual_capture_output = False
                        actual_read_stdout = False

                else:

                    if show_output_on_screen and capture_stdout:
                        actual_command = f"""sudo {env_part} --login bash '{filepath}'"""
                        actual_capture_output = True
                        actual_read_stdout = False
                    elif show_output_on_screen and not capture_stdout:
                        actual_command = f"""sudo {env_part} --login bash '{filepath}'"""
                        actual_capture_output = False
                        actual_read_stdout = False
                    elif not show_output_on_screen and capture_stdout:
                        actual_command = f"""sudo {env_part} --login bash '{filepath}' > {stdout_filepath} 2>{stderr_filepath}"""
                        actual_capture_output = False
                        actual_read_stdout = True
                    else:
                        actual_command = f"""sudo {env_part} --login bash '{filepath}' 2>&1 > /dev/null"""
                        actual_capture_output = False
                        actual_read_stdout = False

            else:
                if show_output_on_screen and capture_stdout:
                    actual_command = f"""sudo {env_part} --user {self.get_current_username()} --login bash '{filepath}'"""
                    actual_capture_output = True
                    actual_read_stdout = False
                elif show_output_on_screen and not capture_stdout:
                    actual_command = f"""sudo {env_part} --user {self.get_current_username()} --login bash '{filepath}'"""
                    actual_capture_output = False
                    actual_read_stdout = False
                elif not show_output_on_screen and capture_stdout:
                    actual_command = f"""sudo {env_part} --user {self.get_current_username()} --login bash '{filepath}' > {stdout_filepath} 2>{stderr_filepath}"""
                    actual_capture_output = False
                    actual_read_stdout = True
                else:
                    actual_command = f"""sudo {env_part} --user {self.get_current_username()} --login bash '{filepath}' 2>&1 > /dev/null"""
                    actual_capture_output = False
                    actual_read_stdout = False

            if log_entry:
                log_method = logging.info
            else:
                log_method = logging.debug
            log_method(f"Executing {actual_command}")
            with open(filepath, "r") as f:
                log_method(f"in file \"{filepath}\" = \n{f.read()}")

            result = subprocess.run(
                args=actual_command,
                cwd=cwd,
                shell=True,
                capture_output=actual_capture_output,
                timeout=timeout,
                env=env
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

    def get_env_variable(self, name: str) -> str:
        exit_code, stdout, _ = self.execute_command(
            commands=[f"printenv {name}"],
            capture_stdout=True,
            show_output_on_screen=False,
            check_exit_code=False,
        )
        if exit_code != 0:
            raise PMakeException(f"Cannot find the environment variable \"{name}\" for user \"{self.get_current_username()}\"")

        return stdout.strip()

    def get_home_folder(self) -> path:
        return self.get_env_variable("HOME")

    def _fetch_interesting_paths(self, script: "SessionScript") -> Dict[str, List[InterestingPath]]:
        return {}

    def set_global_environment_variable(self, group_name: str, name: str, value: Any):
        open()
        file_with_environment = f"/etc/profile.d/{group_name}.sh"
        self.execute_command(
            commands=[f"cat {file_with_environment}"],
            show_output_on_screen=False,
            capture_stdout=True,
            check_exit_code=False,
        )
        self.execute_command(commands=[
            f"""echo 'export {name}="{value}" >> /etc/profile.d/{group_name}.bash""",
        ],
        execute_as_admin=True)

    def is_program_installed(self, program_name: str) -> bool:
        exit_code, _, _ = self.execute_command(
            commands=[f"which {program_name}"],
            show_output_on_screen=False,
            capture_stdout=True,
            check_exit_code=False
        )
        return exit_code == 0
